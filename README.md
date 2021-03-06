# groundfailure

## Introduction

groundfailure is a project designed to implement models for calculating landslide and
liquefaction probability given an input ShakeMap.  

Code documentation: http://usgs.github.io/groundfailure/

*Disclaimer:* This software is preliminary or provisional and is subject to 
revision. It is being provided to meet the need for timely best science. The 
software has not received final approval by the U.S. Geological Survey (USGS).
No warranty, expressed or implied, is made by the USGS or the U.S. Government as
to the functionality of the software and related material nor shall the fact of
release constitute any such warranty. The software is provided on the condition
that neither the USGS nor the U.S. Government shall be held liable for any
damages resulting from the authorized or unauthorized use of the software. 


## Installation and Dependencies

To install this package:

```sh
pip install git+git://github.com/usgs/groundfailure.git
```

To upgrade this package:

```sh
pip install -U git+git://github.com/usgs/groundfailure.git
```

This package depends on a number of other libraries, most of which are installed with Anaconda. 
We strongly suggest that users install Anaconda or one of the other Scipy Stack distributions
described [here](http://www.scipy.org/install.html).

The easiest way to set up your environment is to install Anaconda and then take use the setup script

```sh
setup_env.sh
```

which is included in the repository to set up a 
[virtual environment](http://conda.pydata.org/docs/using/envs.html) using the following command:

```sh
bash setup_env.sh
```

If you don't want to set your system up using an anaconda virtual environment, here is a list of
other dependencies that may not be installed with a distribution:

* configobj
* fiona
* rasterio
* shapely
* gdal
* h5py
* descartes
* scikit-learn

Usually these packages can be installed with either conda (Anaconda installs) or pip. 

Some other third party dependencies can be installed by the following:

```sh
pip install https://github.com/usgs/MapIO/archive/master.zip
```

```sh
pip install https://github.com/usgs/earthquake-impact-utils/archive/master.zip
```

```sh
pip install https://github.com/gem/oq-hazardlib/archive/master.zip
```

```sh
pip install scikit-image
```

```sh
pip install sphinx_rtd_theme
```

```sh
pip install git+git://github.com/python-visualization/folium.git
```

For gdalfuncs to work (find proj.4 libraries), you may need to add the following line to 
your .bash_profile:

```sh
export PROJSO=/Library/Frameworks/PROJ.framework/PROJ
```

To run gfail from the command line, you will need to add its location to your .bash_profile:

```sh
export PATH=~/groundfailure:$PATH
```

## Configuration

For each model, there is a configuration file that describes the model parameters, default values, 
metadata/source details, input file locations, and display preferences. Default versions with relative
file paths are found in the defaultconfigfiles folder of the [repository](https://github.com/usgs/groundfailure/tree/master/defaultconfigfiles).
These can be edited but to avoid overwriting your changes each time you update the groundfailure
codes, you should edit copies outside of the repository.

Default options, such as the output directory, paths to input data files, paths to mapping files etc.
can be specified using gfail, see below for details.

### Using gfail to set default paths on system (gfail must be in system path)

#### set default paths

```sh
gfail --set-default-paths -d full/modelinput/data/path -o full/output/location/filepath
-c full/filepath/to/model/config/files -m full/filepath/to/mapping/config/file -md full/filepath/to/data/for/mapping
```

#### check default paths that are currently set

```sh
gfail --list-default-paths
```

#### clear all default paths

```sh
gfail --reset-default-paths
```

#### after setting default paths, gfail can be run like this:

```sh
gfail modelconfig.ini shakefile.xml -s -pd -pi
```

* the pd flag outputs static pdfs of model results
* the pi flag creates interactive plots as html files
* type gfail -h to see all options

### Model config file format

The config file format is a modified version of the "INI" format.  It is described in detail [here](http://configobj.readthedocs.org/en/latest/configobj.html#config-files):

**Notes** 
* References and other inputs with commas within them need to be enclosed in quotes or else they 
  will not be read in properly (commas will be used to separate) - for example: 
  'Verdin, D.W., Godt, J., Funk, C., Pedreros, D., Worstell, B. and Verdin, J., 2007, 
  Development of a global slope dataset for estimation of landslide occurrence resulting from 
  earthquakes: U.S. Geological Survey Open-File Report 2007–1188, 25p.'
* Arrays should be not be enclosed in brackets and should be comma separated, for example: model = 0, 0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99, 1.
* Files, filepaths, and folders being used for input layers should all be labeled as 'file' in the config file regardless of actual structure.
* If file paths in the config file are relative to a base folder on the users system, and you are
  running models manually and/or not setting default paths in gfail you will need
  to run correct_config_filepaths() after reading in the config file. See notebooks for details.

```ini
[nowicki_2014_global]
  # Detailed description of the model and references.
  description = 'This is the original landslide model of Nowicki et al 2014 using PGA, Slope, Cohesion, and CTI based on global datasets.'
  longref = """Nowicki, M.A., Wald, D.J., Hamburger, M.W., Hearne, Michael, and Thompson, E.M., 2014, Development of a 
            globally applicable model for near real-time prediction of seismically induced landslides: Engineering 
            Geology, v. 173, p. 54–65."""
  shortref = 'Nowicki and others (2014)'
  
  # Ground failure model type, pptions are landslide or liquefaction.
  gfetype = landslide

  # The grid to which all other grids in this model will be resampled
  baselayer = slope

  # Thresholds for filtering results, probabilities will be set to zero below slopemin, above slopemax
  # using the slopefile defined
  slopemin = 5. # in degrees
  slopemax = 90. # in degrees
  slopefile = global_gted_maxslope_30c.flt

  # groundfailure function corresponding to this model
  funcname = LogisticModel

  [[layers]]
    [[[slope]]]
      file = global_Verdin_slopes_resampled_degx100/slope_max.bil
      units = degrees*100
      longref = """Verdin, D.W., Godt, J., Funk, C., Pedreros, D., Worstell, B. and Verdin, J., 2007, Development of a 
                global slope dataset for estimation of landslide occurrence resulting from earthquakes: U.S. Geological 
                Survey Open-File Report 2007–1188, 25p."""
      shortref = 'Verdin et al. (2007)'
    [[[friction]]]
      file = global_friction_deg.flt
      units = degrees
      longref = """Godt, J.W., Sener, B., Verdin, K.L., Wald, D.J., Earle, P.S., Harp, E.L. and Jibson, R.W., 2008, 
                   Rapid Assessment of Earthquake-induced Landsliding: Proceedings of the First World Landslide Forum, 
                   United Nations University, Tokyo, Japan, p. 392-395."""
      shortref = 'Godt and others (2008)'
    [[[cti1]]] # Must use cti1 or else the cti in the word friction will get changed
      file = global_cti_fil.grd
      units = index
      longref = 'USGS HYDRO1k geographic database, available at https://lta.cr.usgs.gov/HYDRO1K'
      shortref = 'HYDRO1k'

  [[interpolations]]
    slope = linear
    friction = nearest
    cti1 = linear

  [[terms]]
    #These terms must be named as b1-bN, where N is the number of coefficients
    #in a logistic regression, which takes the form:
    #1/(1 + e^-eqn)
    #where eqn is a linear equation of the form:
    #b0 + b1*t1 + b2*t2 + ... + bN*tN
    #where t1, t2, ... tN are the right hand side of the parameters below.
    #The terms may include the names of layers and any of the following ShakeMap macros:
    #pga,pgv,mmi,MW
    b1 = pga
    b2 = 'slope / 100.'  # Divide slopes by 100 because Verdin dataset multiplies by 100
    b3 = friction
    b4 = cti1 * 100. # Multiply by 100 because Anna used a layer representing CTI * 100 in her model
    b5 = 'pga * slope / 100.' # Divide slopes by 100 because Verdin dataset multiplies by 100

  [[coefficients]]
    #These coefficients must be named as b1-bN, where N is the number of coefficients
    #in a logistic regression, which takes the form:
    #1/(1 + e^-eqn)
    #where eqn is a linear equation of the form:
    #b0 + b1*t1 + b2*t2 + ... + bN*tN
    #where t1, t2, ... tN are the right hand side of the parameters below.
    b0 = -3.6490 #intercept
    b1 = 0.0133 #pga
    b2 = 0.0364 #slope
    b3 = -0.0635 #friction
    b4 = -0.0004 # cti
    b5 = 0.0019 # pga*slope

  [[display_options]]  # Display preferences for mapping programs (not required)
    [[[lims]]]  # Optional
      # Corresponding to different possible layer keys - don't need these, will just use defaults if missing,
      # don't need full name of layer, just something that is part of it
      model = None
      friction = None
      pga = None
      slope = None
      cti1 = None

    [[[colors]]]
      # use matplotlib colormaps, starting with cm.
      default = cm.jet
      alpha = 0.7
      # Corresponding to different possible layer keys - don't need these, will just use defaults if missing
      model = cm.jet
      friction = cm.jet
      pga = cm.jet
      slope = cm.jet
      cti1 = cm.jet

    [[[logscale]]]
      # Whether to use a log scale in figures for given layer
      # Corresponding to different possible layer keys - don't need these, will just use defaults if missing,
      # don't need full name of layer, just something that is part of it
      model = False
      friction = False
      pga = False
      slope = False
      cti1 = False

    [[[maskthresholds]]]
      # Model result cells with values below this threshold will be masked in plots
      # Corresponding to different possible layer keys - don't need these, will just use defaults if missing,
      # don't need full name of layer, just something that is part of it
      model = 0.05
      friction = 0.
      pga = None
      slope = None
      cti1 = None
```

### Mapping config file format
The mapping config file tells the program what files to use (roads, cities etc.) for creating static maps.
It is not required, but static maps may be bland without these.

```ini
# All map inputs are optional, but desireable. File paths are relative to the mapping_inputs folder
# Default display options for each input layer are found in the model config file

[dem]  # Optional, for making hillshade
  file = md30_gmted_gmt.grd

[roads]  # Optional
  file = roads  # Folder in this case
  longref = """Center for International Earth Science Information Network - CIESIN, 2013, Global Roads Open Access Data Set,
   Version 1 (gROADSv1): Columbia University, and Information Technology Outreach Services - ITOS - University of Georgia,
   Palisades, NY, NASA Socioeconomic Data and Applications Center (SEDAC). http://dx.doi.org/10.7927/H4VD6WCT.""
  shortref = 'CIESIN (2013)"""

[cities]  # Optional
  file = cities1000.txt
  longref = GeoNames, http://geonames.org/ Accessed: 2 Sept 2015
  shortref = GeoNames

[ocean]  # Optional
  file = ne_10m_ocean/ne_10m_ocean.shp
  longref = Natural Earth (acc. 2016)
  shortref = Natural Earth (2016) Ocean polygon http://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-ocean/

[colors]
  # Define basic colors
  roadcolor = 808080
  countrycolor = 474747
  watercolor = B8EEFF

```

## API for Model Output

Each model should output a single dictionary, which has keys that correspond to the names of the 
input and output layers from the model.

Each layer in the dictionary is itself a dictionary, with the following fields:
 - *description* A dictionary with the fields:

   * *name* Short name, suitable for use as a plot title if necessary.
   * *longref* Full citation, USGS format as described here: http://internal.usgs.gov/publishing/sta/sta28.pdf
   * *units* Physical units for input data layers, and one of the following for output "probability" layers:

     * *index* Relative (low to high) index of occurrence in a given cell (not necessarily bounded).
     * *probability* Probability of event (landslide,liquefaction) of a given size occurring in a given cell (0 to 1).
     * *coverage* Fractional coverage of groundfailure in a given cell (0 to 1).
     * *displacement* Distance material will move from or in given cell (unbounded).

   * *parameters* (Not required for input layers) A dictionary of key/value pairs, where the values must be either numbers or strings.

 - *type* Indicates whether this grid contains input data or output from a model.

 - *label* What will be written next to the colorbar for the data layer.

 - *grid* Input data or model output, in the form of a Grid2D object. 

A template model function implementation is shown below.

```py
def failure_model():
    geodict = GeoDict({'xmin':0.5,'xmax':3.5,
                       'ymin':0.5,'ymax':3.5,
                       'dx':1.0,'dy':1.0,
                       'nx':4,'ny':4})
    pgrid = Grid2D(data = np.arange(0,16).reshape(4,4),geodict=geodict)
    cgrid = Grid2D(data = np.arange(1,17).reshape(4,4),geodict=geodict)
    sgrid = Grid2D(data = np.arange(2,18).reshape(4,4),geodict=geodict)
    mgrid = Grid2D(data = np.arange(3,19).reshape(4,4),geodict=geodict)

    modellayer = {'description':{'name':'Nowicki 2014',
                                'longref':'Nowicki, A., 2014, A logistic regression landslide model: Failure Monthly, v. 2, p. 1-7.',
                                'units':'index',
                                'shakemap': '19940117123055_ver2'
                                'parameters':{'b0':1.045,
                                              'b1':5.435}},
                 'type':'output',
                 'label':'Relative Index Value',
                 'grid':pgrid,
                 }
    
    layer1 = {'description':{'name':'Smith and Jones 1994',
                             'longref':'Smith J. and Jones, J., 1994, Holding on to things: Journal of Geophysical Sciences, v. 17,  p. 100-105',
                             'units':'kPa'},
              'type':'input',
              'label':'cohesion (kPa)',
              'grid':cgrid}
    
    layer2 = {'description':{'name':'Garfunkel and Oates 2001',
                             'longref':'Garfunkel, A., and Oates, J., 2001, I'm afraid to look down: Journal of Steepness, v. 8, p. 10-25',
                             'units':'degrees'},
              'type':'input',
              'label':'slope (degrees)',
              'grid':sgrid}

    layer3 = {'description':{'units':'g'
                             'shakemap': '19940117123055_ver2'},
              'type':'input',
              'label':'PGA (g)',
              'grid':mgrid}

    output = {'model':problayer,
              'cohesion':layer1,
              'slope':layer2,
              'pga':layer3}

    return output
```
