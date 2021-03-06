#!/usr/bin/env python

import os.path
import os
from configobj import ConfigObj
import numpy as np
import groundfailure.logisticmodel as LM
from mapio.geodict import GeoDict
from groundfailure.conf import correct_config_filepaths

#hack the path so that I can debug these functions if I need to
#homedir = '/Users/kallstadt/SecondaryHazards/Codes/groundfailure/tests'
homedir = os.path.dirname(os.path.abspath(__file__))  # where is this script?
datadir = os.path.abspath(os.path.join(homedir, 'data'))
#logisticmodeldir = os.path.abspath(os.path.join(homedir, 'groundfailure'))
#sys.path.insert(0, logisticmodeldir)  # put this at the front of the system path, ignoring any installed mapio stuff

configfile = os.path.join(datadir, 'testconfig_logimodel.ini')
config = ConfigObj(configfile)
# Test path correction (from conf.py)
config = correct_config_filepaths(datadir, config)

cmodel = config['test_model']
layers = []

shakefile = os.path.join(datadir, 'test_shakegrid.xml')
uncertfile = os.path.join(datadir, 'test_uncert.xml')
cofile = os.path.join(datadir, 'test_cohesion.bil')
slopefile = os.path.join(datadir, 'test_slope.bil')
vs30file = os.path.join(datadir, 'test_vs30.bil')
ctifile = os.path.join(datadir, 'test_cti1.bil')
precipfolder = os.path.join(datadir, 'test_precip')

fakegeodict = GeoDict({'xmin': 0.5, 'xmax': 1.5,
                      'ymin': 0.5, 'ymax': 1.5,
                      'dx': 1.0, 'dy': 1.0,
                      'ny': 2, 'nx': 2})


def test_logisticmodel():
    #print('Making sure the logistic model runs with and without uncertainty and precipitation - these files are 4x4 cells')
    modelLQ = {'TestModelLQ': {'description': 'This is a test liquefaction model',
                               'gfetype': 'liquefaction',
                               'baselayer': 'vs30',
                               'slopemin': 0.,
                               'slopemax': 5.,
                               'layers': {'vs30': {'file': vs30file, 'units': 'm/s', 'longref': 'more words',
                                                   'shortref': 'words'},
                                          'cti1': {'file': ctifile, 'units': 'unitless',
                                                   'longref': 'more words', 'shortref': 'words'}},
                               'interpolations': {'vs30': 'nearest',
                                                  'cti1': 'linear'},
                               'terms': {'b1': 'log((pga/100.0)*(power(MW,2.)))',
                                         'b2': 'cti1',
                                         'b3': 'log(vs30)'},
                               'coefficients': {'b0': 15.,
                                                'b1': 2.,
                                                'b2': 0.3,
                                                'b3': -4.}}}

    modelLS = {'TestModelLS': {'description': 'This is a test landslide model',
                               'gfetype': 'landslide',
                               'baselayer': 'slope',
                               'slopemin': 5.,
                               'slopemax': 90.,
                               'layers': {'friction': {'file': cofile, 'units': 'kPa',
                                                       'longref': 'more words',
                                                       'shortref': 'words'},
                                          'slope': {'file': slopefile, 'units': 'degrees',
                                                    'longref': 'more words', 'shortref': 'words'},
                                          'precip': {'file': precipfolder, 'units': 'mm',
                                                     'longref': 'more words', 'shortref': 'words'}},
                               'interpolations': {'friction': 'linear', 'slope': 'linear',
                                                  'precip': 'nearest'},
                               'terms': {'b1': 'pga',
                                         'b2': 'slope',
                                         'b3': 'precipMONTH',
                                         'b4': 'pga*slope*MW'},
                               'coefficients': {'b0': -7.,
                                                'b1': 0.06,
                                                'b2': 0.0008,
                                                'b3': 0.02,
                                                'b4': 1.e-05}}}

    ls = LM.LogisticModel(shakefile, modelLS, uncertfile=None, slopefile=slopefile)
    LS = ls.calculate()

    lsu = LM.LogisticModel(shakefile, modelLS, uncertfile=uncertfile, slopefile=slopefile)
    try:
        lsu.getEquation()
        lsu.getEquations()
    except Exception as e:
        print(e)
        print('LogisticModel.getEquation and/or LogisticModel.getEquations did not work')
    LSU = lsu.calculate()

    lq = LM.LogisticModel(shakefile, modelLQ, uncertfile=None, saveinputs=True)
    LQ = lq.calculate()

    # See if getGeoDict works
    assert(ls.getGeoDict() == fakegeodict), 'getGeoDict did not return the geodict expected'

    targetLS = np.array([[0.61358336819225268, 0.99999969213372109], [0.50746944427265206, 0.010791994705496567]])
    targetLSU = np.array([[0.48852712099785173, 0.99999827441447309], [0.28923565862849882, 0.0097842502221282737]])
    targetLQ = np.array([[0.5803309852347005, 0.27771418649141888], [0.053465704369553384, 0.013015247124965424]])

    # Check if results are as expected by manual calculation
    np.testing.assert_allclose(LS['model']['grid'].getData(), targetLS, rtol=1e-05)
    np.testing.assert_allclose(LSU['modelmin']['grid'].getData(), targetLSU, rtol=1e-05)  # Need to check one of the uncertainties at least
    np.testing.assert_allclose(LQ['model']['grid'].getData(), targetLQ, rtol=1e-05)


def test_getLogisticModelNames():
    names = LM.getLogisticModelNames(config)
    assert('test_model' in names), 'getLogisticModelNames did not return expected result'


def test_validateCoefficients():
    data = {'b0': 3.5, 'b1': 0.3, 'b2': 2.1, 'b3': -0.5, 'b4': 0.01, 'b5': 1.0}
    coeff = LM.validateCoefficients(cmodel)
    assert(data == coeff), 'logisticmodel.validateCoefficients did not return expected result'


def test_validateLayers():
    data = {'cti1': os.path.join(datadir, 'test_cti1.bil'),
            'friction': os.path.join(datadir, 'test_friction.bil'),
            'precip': [os.path.join(datadir, 'test_precip/prec_Jan.bil')],
            'slope': os.path.join(datadir, 'test_slope.bil'),
            'vs30': os.path.join(datadir, 'test_vs30.bil')}
    layers = LM.validateLayers(cmodel)
    assert(data == layers), 'validateLayers did not return expected result'


def test_validateTerms():
    data = {'b1': "np.nan_to_num(self.layerdict['friction'].getData())", 'b2': "self.layerdict['slope'].getData()/100.",
            'b3': "np.log(self.layerdict['vs30'].getData())", 'b4': "self.layerdict['cti1'].getData()",
            'b5': "self.layerdict['precip'].getData()"}
    timeField = 'MONTH'
    coeff = LM.validateCoefficients(cmodel)
    layers = LM.validateLayers(cmodel)
    terms, time = LM.validateTerms(cmodel, coeff, layers)
    assert(time == timeField), 'validateTerms did not return expected timeField'
    assert(data == terms), 'validateTerms did not return expected terms'


def test_validateInterpolations():
    data = {'cti1': 'nearest',
            'friction': 'nearest',
            'precip': 'nearest',
            'slope': 'nearest',
            'vs30': 'nearest'}
    layers = LM.validateLayers(cmodel)
    interp = LM.validateInterpolations(cmodel, layers)
    assert(data == interp), 'validateInterpolations did not return expected dictionary'


def test_validateUnits():
    data = {'cti1': 'unitless',
            'friction': 'degrees',
            'precip': 'mm',
            'slope': 'degrees',
            'vs30': 'm/s'}
    layers = LM.validateLayers(cmodel)
    interp = LM.validateUnits(cmodel, layers)
    assert(data == interp), 'validateInterpolations did not return expected dictionary'


def test_validateLogisticModels():
    LM.validateLogisticModels(config)


def test_validateRefs():
    fakemr = {'longref': 'full reference', 'shortref': 'Name et al. year'}
    fakelr = {'cti1': 'longref',
              'friction': 'longref',
              'precip': 'longref',
              'slope': 'longref',
              'vs30': 'longref'}
    fakesr = {'cti1': 'shortref',
              'friction': 'shortref',
              'precip': 'shortref',
              'slope': 'shortref',
              'vs30': 'shortref'}
    modelrefs, longrefs, shortrefs = LM.validateRefs(cmodel)
    assert(fakemr == modelrefs), 'validateRefs did not return expected list of modelrefs'
    assert(fakelr == longrefs), 'validateRefs did not return expected list of longrefs'
    assert(fakesr == shortrefs), 'validateRefs did not return expected list of shortrefs'


def test_checkTerm():
    term1 = 'precipMONTH'
    layers = LM.validateLayers(cmodel)
    term, tterm, timeField = LM.checkTerm(term1, layers)
    assert(term == "self.layerdict['precip'].getData()" and tterm == '' and timeField == 'MONTH'), 'checkTerm did not work properly for precipMonth'
    term2 = 'MWextrajunk'
    term, tterm, timeField = LM.checkTerm(term2, layers)
    assert(term == "self.shakemap.getEventDict()['magnitude']extrajunk" and tterm == 'extrajunk'), 'checkTerm did not identify extrajunk in MWextrajunk term'

if __name__ == "__main__":
    test_logisticmodel()
    test_getLogisticModelNames()
    test_validateCoefficients()
    test_validateLayers()
    test_validateTerms()
    test_validateInterpolations()
    test_validateUnits()
    test_validateLogisticModels()
    test_validateRefs()
    test_checkTerm()
    print('logisticmodel.py tests passed')
