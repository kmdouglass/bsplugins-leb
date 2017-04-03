# © All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE,
# Switzerland, Laboratory of Experimental Biophysics, 2016
# See the LICENSE.txt file for more details.
"""B-Store extensions used by the Laboratory of Experimental Biophysics.

"""
import bstore.parsers as pr
import bstore.config
import pathlib, sys, importlib, re, warnings

class MMParser(pr.Parser):
    """Parses a LEB Micro-Manager-based file for the acquisition info.
        
    References
    ----------
    1. https://pypi.python.org/pypi/tifffile
    
    Attributes
    ----------
    channelIdentifier   : dict
        All of the channel identifiers that the MMParser recognizes.
    initialized         : bool
        Indicates whether the Parser currently possesses parsed information.
    requiresConfig      : bool
        Does parser require configuration before use?
    widefieldIdentifier : str
        The string identifying the widefield image number.
    
    """
    # This dictionary contains all the channel identifiers MMParser
    # knows natively.
    channelIdentifier = {
        'A488' : 'AlexaFluor 488',
        'A647' : 'AlexaFluor 647',
        'A750' : 'AlexaFluor 750',
        'DAPI' : 'DAPI',
        'Cy5'  : 'Cy5'}
                         
    # All identifiers of a widefield image in a file name.
    widefieldIdentifier = ['WF']
    
    def __init__(self):
        # Start uninitialized because parseFilename has not yet been called
        self.initialized   = False
    
    @property
    def dataset(self):
        if self.initialized:
            return self._dataset
        else:
            raise pr.ParserNotInitializedError('Error: No dataset is parsed.')
    
    @dataset.setter
    def dataset(self, ds):
        self._dataset = ds
        
    @property
    def initialized(self):
        return self._initialized
        
    @initialized.setter
    def initialized(self, value):
        """Resets the Parser to an uninitialized state if True is provided.
        
        Parameters
        ----------
        value : bool
        """
        if isinstance(value, bool):
            self._initialized = value
            
            if value == False:
                self.dataset = None
        else:
            raise ValueError('Error: initialized must be a bool.')
            
    @property
    def requiresConfig(self):
        return False

    def parseFilename(
            self, filename, datasetType = 'Localizations',
            readData=True, **kwargs):
        """Parse the filename to extract the acquisition information.
        
        Running this method will reset the parser to an uninitialized state
        before initializing it with the new data.
        
        Parameters
        ----------
        filename        : str or Path
            A string or pathlib Path object containing the dataset's filename.
        datasetType     : str
            One of the registered datasetTypes.
        readData        : bool
            Determines whether data will be read from the file.
            
        """
        # Reset the parser
        self.initialized = False   
        
        if datasetType not in bstore.config.__Registered_DatasetTypes__:
            raise pr.DatasetTypeError(
                '{} is not a registered type.'.format(datasetType)) 
        
        # Convert Path objects to strings
        if isinstance(filename, pathlib.PurePath):
            fullPath = filename
            filename = str(filename.name)
        elif isinstance(filename, str):
            fullPath = pathlib.Path(filename)
            filename = str(fullPath.name)
        else:
            raise TypeError('Unrecognized type for filename.')
        
        # Used to access data
        self._filename = filename
        self._fullPath = fullPath
        
        try:
            # Do parsing for particular types here
            if datasetType   == 'WidefieldImage':
                parsedData = self._parseWidefieldImage(filename)
            else:
                parsedData = self._parse(filename)
        except:
            raise pr.ParseFilenameFailure(
                ('Error: File could not be parsed.', sys.exc_info()[0]))
        
        # Build the return dataset
        prefix, acqID, channelID, dateID, posID, sliceID = parsedData
        idDict = {'prefix' : prefix, 'acqID' : acqID, 'channelID' : channelID,
                  'dateID' : dateID, 'posID' : posID, 'sliceID' : sliceID}
        
        mod   = importlib.import_module('bstore.datasetTypes.{0:s}'.format(
                                                                  datasetType))
        dType = getattr(mod, datasetType)
            
        self.dataset = dType(datasetIDs = idDict)
        
        # Parser is now set and initialized.
        self.initialized = True

        try:
            if readData:
                self.dataset.data = self.dataset.readFromFile(
                                        self._fullPath, **kwargs)
            else:
                self.dataset.data = None
        except:
            warnings.warn('Warning: Filename successfully parsed, but no data '
                          'was read from the file.')
        
    def _parse(self, filename, extractAcqID = True):
        """Parse a generic file, i.e. one not requiring special treatment.
        
        Parameters
        ----------
        filename     : str
            The filename for the current file to parse.
        extractAcqID : bool
            Should an acquisition ID be extracted from the filename? This
            is useful for widefield images because they will not contain
            an acquisition ID that is automatically inserted into the
            filename.
            
        Returns
        -------
        prefix    : str
        acqID     : int
        channelID : str
        dateID    : str
        posID     : (int,) or (int, int)
        sliceID   : int
        
        """
        # Remove any leading underscores
        filename = filename.lstrip('_')        
        
        # Split the string at 'MMStack'
        prefixRaw, suffixRaw = filename.split('_MMStack_')         
            
        # Obtain the acquisition ID
        prefixRawParts = prefixRaw.split('_')
        if extractAcqID:
            acqID          = int(prefixRawParts[-1])
            prefix    = '_'.join(prefixRawParts[:-1])
        else:
            # This must be set elsewhere, such as by a widefield image
            # tag. Not setting it results in an error when instantiating
            # a Dataset instance.
            acqID  = None
            
            # Cannot simply use prefixRaw because spurious underscores
            # will survive through into prefix
            prefix = '_'.join(prefixRawParts)
        
        # Obtain the channel ID and prefix
        # Extract any channel identifiers if present using
        # channelIdentifer dict
        prefix    = re.sub(r'\_\_+', '_', prefix) # Remove repeats of '_'
        channelID = [channel for channel in self.channelIdentifier.keys()
                     if channel in prefix]
        assert (len(channelID) <= 1), channelID
        try:
            channelID       = channelID[0]
            channelIDString = re.search(r'((\_' + channelID +              \
                                            ')\_?$)|((^\_)?' + channelID + \
                                            '(\_)?)',
                                        prefix)
            prefix = prefix.replace(channelIDString.group(), '')
        except IndexError:
            # When there is no channel identifier found, set it to None
            channelID = None
    
        # Obtain the position ID using regular expressions
        # First, extract strings like 'Pos0' or 'Pos_003_002
        positionRaw = re.search(r'Pos\_\d{1,3}\_\d{1,3}|Pos\d{1,}', suffixRaw)
        if positionRaw == None:
            posID = None
        else:
            # Next, extract the digits and convert them to a tuple
            indexes = re.findall(r'\d{1,}', positionRaw.group(0))
            posID   = tuple([int(index) for index in indexes])
             
        # These are not currently implemented by the MMParser
        sliceID = None
        dateID  = None
        
        # PyTables has problems with spaces in the name
        prefix = prefix.replace(' ', '_')        
        
        return prefix, acqID, channelID, dateID, posID, sliceID
        
    def _parseWidefieldImage(self, filename):
        """Parse a widefield image for the Dataset interface.
        
        Parameters
        ----------
        filename : str
            The filename for the current file to parse.
            
        Returns
        -------
        prefix    : str
        acqID     : int
        channelID : str
        dateID    : str
        posID     : (int,) or (int, int)
        sliceID   : int
            
        """
        prefix, acqID, channelID, dateID, posID, sliceID = \
                        self._parse(filename, extractAcqID = False)
                        
        # Extract the widefield image identifier from prefix and use it
        # to set the acquisition ID. See the widefieldIdentifier dict.
        wfID = [wfFlag for wfFlag in self.widefieldIdentifier
                if wfFlag in prefix]
        assert (len(wfID) <= 1), wfID
        try:
            wfID       = wfID[0]
            wfIDString = re.search(r'((\_' + wfID +                \
                                   '\_?\d+)\_?$)|((^\_)?' + wfID + \
                                   '\_*\d+(\_?))', prefix)
            prefix = prefix.replace(wfIDString.group(), '')
        except IndexError:
            # When there is no widefield identifier found, set
            # acqID to None
            warnings.warn(
                'Warning: No widefield ID detected in {0:s}.'.format(prefix)
                )
            acqID = None
        else:
            acqID = re.findall(r'\d+', wfIDString.group())
            assert len(acqID) == 1, 'Error: found multiple acqID\'s.'
            acqID = int(acqID[0])
            
        return prefix, acqID, channelID, dateID, posID, sliceID