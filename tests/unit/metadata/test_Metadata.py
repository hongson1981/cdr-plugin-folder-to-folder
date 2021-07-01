
from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import temp_file, file_delete, folder_exists, file_exists, path_combine, folder_not_exists, \
    file_copy, parent_folder, file_name

from cdr_plugin_folder_to_folder.metadata.Metadata import Metadata, DEFAULT_METADATA_FILENAME
from cdr_plugin_folder_to_folder.metadata.Metadata_Utils import Metadata_Utils


class test_Metadata(TestCase):
    file_path      = None
    file_copy_path = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.file_path      = temp_file(contents='some text')                        # test file
        cls.file_copy_path = cls.file_path + '_an_copy'                             # create a copy to test adding multiple files
        file_copy(cls.file_path, cls.file_copy_path)

    @classmethod
    def tearDownClass(cls) -> None:
        file_delete(cls.file_path)
        file_delete(cls.file_copy_path)

    def setUp(self) -> None:
        self.file_hash      = 'b94f6f125c79e3a5ffaa826f584c10d52ada669e6762051b826b55776d05aed2'
        self.metadata       = Metadata()
        self.metadata_utils = Metadata_Utils()

    def test_add_file(self):
        metadata   = self.metadata
        file_paths = metadata.data.get('original_file_paths')

        assert self.metadata.exists() is False                          # metadata folder doesn't exist

        # adding file first time
        assert metadata.add_file(self.file_path) == self.file_hash                              # add file and get file hash as return value
        assert metadata.exists() is True                                                        # confirm metadata folder now exists
        assert folder_exists(metadata.metadata_folder_path())                                   # confirm metadata folder now exists
        assert file_exists  (metadata.metadata_file_path  ())                                   # confirm metadata json file exists
        assert file_exists  (metadata.source_file_path()    )                                   # confirm source file was correctly put in place
        assert metadata.file_hash == self.metadata_utils.file_hash(metadata.source_file_path()) # confirm hash of source file matches hash of file_path
        assert metadata.metadata_file_path() == path_combine(metadata.metadata_folder_path(),
                                                             DEFAULT_METADATA_FILENAME)         # confirm metadata file is place in correct location
        file_paths = metadata.data.get('original_file_paths')
        assert file_paths == [self.file_path]                                                   # confirms that in this mode the entire path is preserved

        # adding same file 2nd time (with same hash and same name)
        assert metadata.add_file(self.file_path) == self.file_hash                              # adding the same file again
        file_paths = metadata.data.get('original_file_paths')
        assert file_paths == [self.file_path]                                                   # should not impact this value (same as above)

        # adding same file 3nd time (with same hash but different name)
        assert metadata.add_file(self.file_copy_path) == self.file_hash                         # adding the same file again (with different name)
        file_paths = metadata.data.get('original_file_paths')
        assert file_paths == [self.file_path, self.file_copy_path]                              # will make the new file path be added

        # adding same file 4th time (with self.path_hd1 set to parent folder of path)
        file_parent_folder     = parent_folder(self.file_path)                                  # get parent folder of test file
        self.metadata.path_hd1 = file_parent_folder                                             # assign it to the metadata variable used to calculate virtual paths

        assert metadata.add_file(self.file_path) == self.file_hash
        file_paths = metadata.data.get('original_file_paths')
        assert file_paths == [self.file_path, self.file_copy_path, file_name(self.file_path)]   # confirm that the virtual file path was added as the 3rd item (in this case the file name)

        #clean up
        assert self.metadata.delete() is True
        assert folder_not_exists(self.metadata.metadata_folder_path())

    def test_add_file_path(self):
        test_path_1 = path_combine(self.metadata.path_hd1, 'aaaa.txt'    )
        test_path_2 = path_combine(self.metadata.path_hd1, 'bbbb/ccc.txt')
        test_path_3 = 'dddd/eeee.txt'
        test_path_4 = '/fff/gggg.txt'

        file_paths = self.metadata.data.get('original_file_paths')

        assert file_paths == []
        self.metadata.add_file_path(test_path_1)
        assert file_paths == []

        self.metadata.file_hash = 'this value needs to be set for .add_file_path to work'

        self.metadata.add_file_path(test_path_1)
        self.metadata.add_file_path(test_path_2)
        self.metadata.add_file_path(test_path_3)
        self.metadata.add_file_path(test_path_4)
        assert file_paths == ['aaaa.txt', 'bbbb/ccc.txt', 'dddd/eeee.txt', '/fff/gggg.txt']



    def test_delete(self):
        assert self.metadata.delete() is False

    def test_add_file_after_delete_should_not_fail(self):
        metadata = self.metadata
        # adding file first time
        assert metadata.add_file(self.file_path) == self.file_hash                              # add file and get file hash as return value
        assert metadata.exists() is True                                                        # confirm metadata folder now exists
        file_delete(self.metadata.metadata_file_path())                                         # Delete the metadata.json path
        assert metadata.add_file(self.file_path) == self.file_hash                              # Try to add file again, this should not fail
        assert metadata.exists() is True

        #clean up
        assert self.metadata.delete() is True
        assert folder_not_exists(self.metadata.metadata_folder_path())

    def test_metadata_file_path(self):
        assert self.metadata.metadata_folder_path() is None
