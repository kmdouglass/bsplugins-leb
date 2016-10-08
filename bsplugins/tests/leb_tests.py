# © All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE,
# Switzerland, Laboratory of Experimental Biophysics, 2016
# See the LICENSE.txt file for more details.

"""Unit tests for the lebext module.

Notes
-----
nosetests should be run in the project root directory.
 
"""

__author__ = 'Kyle M. Douglass'
__email__ = 'kyle.m.douglass@gmail.com' 

from nose.tools import assert_equal, raises, ok_

# Register the test generic
from bstore import config
config.__Registered_DatasetTypes__.append('TestType')
config.__Registered_DatasetTypes__.append('Localizations')
config.__Registered_DatasetTypes__.append('WidefieldImage')
config.__Registered_DatasetTypes__.append('LocMetadata')

from bstore import parsers, database
from pathlib import Path

testDataRoot = Path(config.__Path_To_Test_Data__)

def test_MMParser_ParseGenericFile():
    """Will MMParser properly extract the acquisition information?
    
    """
    inputFilename   = 'Cos7_Microtubules_A647_3_MMStack_Pos0_locResults.dat'
    datasetType     = 'TestType'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFilename, datasetType)
    assert_equal(mmParser.dataset.datasetIDs['acqID'],                    3)
    assert_equal(mmParser.dataset.datasetIDs['channelID'],           'A647')
    assert_equal(mmParser.dataset.datasetIDs['posID'],                 (0,))
    assert_equal(mmParser.dataset.datasetIDs['prefix'], 'Cos7_Microtubules')
    assert_equal(mmParser.dataset.datasetType,                   'TestType')

@raises(parsers.DatasetTypeError)
def test_MMParser_UnregisteredType_WillNot_Parse():
    """Unregistered datasetTypes should raise an error if parsed.
    
    """
    inputFilename   = 'Cos7_Microtubules_A647_3_MMStack_Pos0_locResults.dat'
    datasetType     = 'Localizations_Cool'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFilename, datasetType)
 
def test_MMParser_Channel_Underscores():
    """Will MMParser extract the prefix and channel with weird underscores?
    
    """
    inputFilename = ['Cos7_Microtubules_Cy5_3_MMStack_Pos0_locResults.dat',
                     '_Cy5_Cos7_Microtubules_3_MMStack_Pos0_locResults.dat',
                     'Cy5_Cos7_Microtubules_3_MMStack_Pos0_locResults.dat',
                     'Cos7_Cy5_Microtubules_3_MMStack_Pos0_locResults.dat',
                     'Cos7_MicrotubulesCy5_3_MMStack_Pos0_locResults.dat',
                     'Cos7_Microtubules__Cy5_3_MMStack_Pos0_locResults.dat',
                     'Cos7___Microtubules__Cy5_3_MMStack_Pos0_locResults.dat']
    datasetType   = 'TestType'
    
    mmParser = parsers.MMParser()
    for currFilename in inputFilename:
        mmParser.parseFilename(currFilename, datasetType)
        assert_equal(mmParser.dataset.datasetIDs['acqID'],                   3)
        assert_equal(mmParser.dataset.datasetIDs['channelID'],           'Cy5')
        assert_equal(mmParser.dataset.datasetIDs['posID'],                (0,))
        assert_equal(mmParser.dataset.datasetIDs['prefix'],'Cos7_Microtubules')
        assert_equal(mmParser.dataset.datasetType,                  'TestType')
  
def test_MMParser_Attributes_NoChannel():
    """Will MMParser extract the acquisition info w/o a channel identifier?
    
    """
    inputFilename   = 'Cos7_Microtubules_12_MMStack_Pos1_locResults.dat'
    datasetType     = 'TestType'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFilename, datasetType)
    assert_equal(mmParser.dataset.datasetIDs['acqID'],                      12)
    assert_equal(mmParser.dataset.datasetIDs['posID'],                    (1,))
    assert_equal(mmParser.dataset.datasetIDs['prefix'],    'Cos7_Microtubules')
    assert_equal(mmParser.dataset.datasetType,                      'TestType')
    assert_equal(mmParser.dataset.datasetIDs['channelID'],                None)
   
def test_MMParser_Attributes_NoPosition():
    """Will MMParser extract the acquisition info w/o a position identifier?
    
    """
    inputFilename   = 'Cos7_Microtubules_12_MMStack_locResults.dat'
    datasetType     = 'TestType'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFilename, datasetType)
    assert_equal(mmParser.dataset.datasetIDs['acqID'],                      12)
    assert_equal(mmParser.dataset.datasetIDs['posID'],                    None)
    assert_equal(mmParser.dataset.datasetIDs['prefix'],    'Cos7_Microtubules')
    assert_equal(mmParser.dataset.datasetType,                      'TestType')
    assert_equal(mmParser.dataset.datasetIDs['channelID'],                None)
  
def test_MMParser_Attributes_MultipleXY():
    """Will MMParser extract multiple xy positions?
    
    """
    inputFilename   = 'HeLa_Actin_4_MMStack_1-Pos_012_003_locResults.dat'
    datasetType     = 'TestType'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFilename, datasetType)
    assert_equal(mmParser.dataset.datasetIDs['acqID'],             4)
    assert_equal(mmParser.dataset.datasetIDs['channelID'],      None)
    assert_equal(mmParser.dataset.datasetIDs['posID'],        (12,3))
    assert_equal(mmParser.dataset.datasetIDs['prefix'], 'HeLa_Actin')
    assert_equal(mmParser.dataset.datasetIDs['sliceID'],        None)
    assert_equal(mmParser.dataset.datasetType,            'TestType')
 
def test_MMParser_Path_Input():
    """Will MMParser properly convert Path inputs to strings?
    
    """
    inputFile = \
        Path('results/Cos7_Microtubules_A750_3_MMStack_Pos0_locResults.dat')
    datasetType = 'TestType'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFile, datasetType)
    assert_equal(mmParser.dataset.datasetIDs['acqID'],                       3)
    assert_equal(mmParser.dataset.datasetIDs['channelID'],              'A750')
    assert_equal(mmParser.dataset.datasetIDs['posID'],                    (0,))
    assert_equal(mmParser.dataset.datasetIDs['prefix'],    'Cos7_Microtubules')
    assert_equal(mmParser.dataset.datasetIDs['sliceID'],                  None)
    assert_equal(mmParser.dataset.datasetType,                      'TestType')
                                                                    
def test_MMParser_Widefield_Attributes():
    """Will MMParser properly extract information from a widefield image?
    
    """
    f = [
        'HeLa_Control_A647_WF13_MMStack_Pos0.ome.tif',
        'HeLa_WF13_Control_A647_MMStack_Pos0.ome.tif',
         'WF13_HeLa_Control_A647_MMStack_Pos0.ome.tif',
        'HeLa_Control_A647_WF13__MMStack_Pos0.ome.tif',
        '_WF13_HeLa_Control_A647_MMStack_Pos0.ome.tif',
        '_WF13_HeLa_Control_A647_MMStack_Pos0.ome.tif',
        'HeLa_Control_A647_WF13_MMStack_Pos0.ome.tif',
        'HeLa_Control_A647_WF_13_MMStack_Pos0.ome.tif',
        'HeLa_WF__13_Control_A647_MMStack_Pos0.ome.tif'
    ]    
    
    mmParser = parsers.MMParser()
    for filename in f:
        mmParser.parseFilename(filename, 'WidefieldImage')
        assert_equal(mmParser.dataset.datasetIDs['acqID'],                  13)
        assert_equal(mmParser.dataset.datasetIDs['channelID'],          'A647')
        assert_equal(mmParser.dataset.datasetIDs['posID'],                (0,))
        assert_equal(mmParser.dataset.datasetIDs['prefix'],     'HeLa_Control')
        assert_equal(mmParser.dataset.datasetIDs['sliceID'],              None)
        assert_equal(mmParser.dataset.datasetType,            'WidefieldImage')
    
def test_MMParser_Widefield_NoChannel():
    """Will MMParser properly extract widefield info w/o a channel?
    
    """
    f = [
        'HeLa_Control_WF13_MMStack_Pos0.ome.tif',
        'HeLa_WF13_Control_MMStack_Pos0.ome.tif',
         'WF13_HeLa_Control_MMStack_Pos0.ome.tif',
        'HeLa_Control_WF13__MMStack_Pos0.ome.tif',
        '_WF13_HeLa_Control_MMStack_Pos0.ome.tif',
        '_WF13_HeLa_Control_MMStack_Pos0.ome.tif',
        'HeLa_Control_WF13_MMStack_Pos0.ome.tif',
        'HeLa_Control_WF_13_MMStack_Pos0.ome.tif',
        'HeLa_WF__13_Control_MMStack_Pos0.ome.tif'
    ]    
    
    mmParser = parsers.MMParser()
    for filename in f:
        mmParser.parseFilename(filename, 'WidefieldImage')
        assert_equal(mmParser.dataset.datasetIDs['acqID'],                  13)
        assert_equal(mmParser.dataset.datasetIDs['channelID'],            None)
        assert_equal(mmParser.dataset.datasetIDs['posID'],                (0,))
        assert_equal(mmParser.dataset.datasetIDs['prefix'],     'HeLa_Control')
        assert_equal(mmParser.dataset.datasetIDs['sliceID'],              None)
        assert_equal(mmParser.dataset.datasetType,            'WidefieldImage')
   
def test_MMParser_Widefield_Bizarre_Underscores():
    """Will MMParser correctly parse this name with bizarre underscores?
    
    """
    filename = '__HeLa_Control__FISH___WF__173_MMStack_Pos0.ome.tif'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(filename, 'WidefieldImage')
    assert_equal(mmParser.dataset.datasetIDs['acqID'],                     173)
    assert_equal(mmParser.dataset.datasetIDs['channelID'],                None)
    assert_equal(mmParser.dataset.datasetIDs['posID'],                    (0,))
    assert_equal(mmParser.dataset.datasetIDs['prefix'],    'HeLa_Control_FISH')
    assert_equal(mmParser.dataset.datasetIDs['sliceID'],                  None)
    assert_equal(mmParser.dataset.datasetType,                'WidefieldImage')
    
def test_MMParser_Dataset():
    """MMParser returns the correct Dataset.
    
    """
    f = 'HeLa_Control_A750_1_MMStack_Pos0_locMetadata.json'
    inputFile = testDataRoot / Path('parsers_test_files') / Path(f)
    datasetType = 'LocMetadata'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFile, datasetType)
    ds = mmParser.dataset
    
    ok_(isinstance(ds, database.Dataset))
    assert_equal(ds.datasetIDs['acqID'],                                     1)
    assert_equal(ds.datasetIDs['channelID'],                            'A750')
    assert_equal(ds.datasetIDs['posID'],                                  (0,))
    assert_equal(ds.datasetIDs['prefix'],                       'HeLa_Control')
    assert_equal(ds.datasetIDs['sliceID'],                                None)
    assert_equal(ds.datasetType,                                 'LocMetadata')
    
    # Test a few metadata entries
    ds.data = ds.readFromFile(inputFile)
    assert_equal(ds.data['Slices'],                                          1)
    assert_equal(ds.data['InitialPositionList'],                          None)
    assert_equal(ds.data['PixelType'],                                 'GRAY8')
    assert_equal(ds.data['Positions'],                                       1)

@raises(parsers.ParserNotInitializedError)    
def test_MMParser_Uninitialized():
    """Will MMParser throw an error when prematurely accessing the dataset?
    
    """
    mmParser = parsers.MMParser()
    mmParser.dataset
 
@raises(parsers.ParserNotInitializedError)    
def test_MMParser_Uninitialized_After_Use():
    """Will MMParser throw an error if dataset is accessed after uninit'ing?
    
    """
    f = 'HeLa_Control_A750_1_MMStack_Pos0_locMetadata.json'
    inputFile   = testDataRoot / Path('parsers_test_files') / Path(f)
    datasetType = 'LocMetadata'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFile, datasetType)
    mmParser.dataset
    
    mmParser.initialized = False
    mmParser.dataset

   
def test_MMParser_Widefield_Data():
    """MMParser correctly loads widefield image data.
    
    """
    f = 'Cos7_A647_WF1_MMStack_Pos0.ome.tif'
    inputFile   = testDataRoot / Path('parsers_test_files') \
                               / Path('Cos7_A647_WF1/') / Path(f)
    datasetType = 'WidefieldImage'
    
    mmParser = parsers.MMParser()
    mmParser.parseFilename(inputFile, datasetType)
    
    ds      = mmParser.dataset   
    ds.data = ds.readFromFile(inputFile)
    
    assert_equal(ds.data.shape, (512, 512))

def test_MMParser_ConvertsSpacesToUnderscores():
    """The MMParser will convert spaces in the prefix to underscores.
    
    """
    # Note the space in prefix!
    f = 'my dataset_A647_1_MMStack_Pos0_locResults.dat'    
    
    parser = parsers.MMParser()
    parser.parseFilename(f, 'TestType')
    assert_equal(parser.dataset.datasetIDs['acqID'],                  1)
    assert_equal(parser.dataset.datasetIDs['channelID'],         'A647')
    assert_equal(parser.dataset.datasetIDs['posID'],               (0,))
    
    # The space should now be an underscore
    assert_equal(parser.dataset.datasetIDs['prefix'],      'my_dataset')
    assert_equal(parser.dataset.datasetType,                 'TestType')

@raises(parsers.ParseFilenameFailure)    
def test_MMParser_ParseFailure():
    """MMParser raises a ParseFilenameFailure error when the filename is bad.
    
    """
    f = 'blablabla 214'
    
    parser = parsers.MMParser()
    parser.parseFilename(f, 'TestType')