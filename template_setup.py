from __future__ import annotations  # allows Folder to reference itself as a type
import os
import pandas as pd
from typing import Optional, List, Dict  # Optional is a type that could be None


def wrap(target: str, wrapping_str: str) -> str:
    """
    This function takes a target string like 'Title' and wraps the wrapping_string around it like '**Title**'
    Meant for simplifying markdown text
    """
    return "".join([wrapping_str, target, wrapping_str])


class Folder:
    def __init__(self, folder_name: str, parent: Optional[Folder], readme_text: Optional[str]) -> None:
        self.parent: Optional[Folder] = parent
        self.readme_text: Optional[str] = readme_text
        try:
            # Make sure that the folder name follows valid conventions
            reserved_chars: List[str] = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            reserved_names: List[str] = ['CON', 'PRN', 'AUX'] + ['COM' + str(i) for i in range(1, 10)] + ['LPT' + str(i) for i in range(1, 10)]
            if any([reserved_chars[i] in folder_name for i in range(len(reserved_chars))]):
                raise Exception('ReservedCharError')
            if any([reserved_names[i] in folder_name for i in range(len(reserved_names))]):
                raise Exception('ReservedNameError')
            self.folder_name: str = folder_name
            self.folder_name.replace(' ', '_')  # remove spaces
            if parent is None:
                self.folder_name = '.'  # this is the root directory for the project, overwrite any user input
        except Exception as err:
            if err.args == 'ReservedCharError':
                print('A reserved character ({0}) was used. Initialization Failed'.format(', '.join(reserved_chars)))
                return
            elif err.args == 'ReservedNameError':
                print('A reserved name ({0}) was used. Initialization Failed'.format(', '.join(reserved_names)))
                return
            else:
                print('Other unexpected error occurred: {0}'.format(err))
                return
        if self.parent is not None:  # trying to create the root directory will raise FileExistsError
            self.create_folder()

    @property  # info on this decorator: https://www.journaldev.com/14893/python-property-decorator
    def folder_path(self) -> str:
        """This function acts as an attribute to get the file path of this Folder object relative to project root"""
        # Can be coded recursively, but I'll use a while loop
        path: List[str] = [self.folder_name]
        folder_parent: Folder = self.parent
        while folder_parent is not None:
            path.append(folder_parent.folder_name)
            # walk up the folder tree to get the name of the next
            folder_parent = folder_parent.parent
        path.reverse()  # reverse the order of the folder name list so the root is first
        path_str: str = '/'.join(path)  # join together the paths with '/' characters
        return path_str

    def create_folder(self) -> None:
        try:
            os.mkdir(self.folder_path)
        except FileExistsError as err:
            print(err)
        if self.readme_text is None:
            return
        with open(self.folder_path + '/README_' + self.folder_name.capitalize() + '.md', 'w') as f:
            f.write('##' + wrap(self.folder_name.capitalize(), '**') + '\n\n')
            f.write('Folder path: ' + wrap(self.folder_path, '`') + '\n\n')
            f.write(self.readme_text)


class ProjectTemplate:
    def __init__(self, template_file: str) -> None:
        self._template_file: str = template_file
        self._df: pd.Dataframe = pd.read_csv(template_file)
        self._folder_tree: Dict[str, Folder] = {'root': Folder('root', None, None)}

    def create_project_tree(self, minimal: bool = False) -> bool:
        creation_success: bool = True  # assume the tree will be created successfully until an error flags this as false
        for i in range(self._df.shape[0]):
            folder_add_flag = False # assume the folder hasn't been added to the tree until it is marked true in 'else:'
            while not folder_add_flag:
                try:
                    if not minimal or (self._df.at[i, 'minimal'] and minimal):  # see Karnaugh map
                        self._folder_tree[self._df.at[i, 'folder_name']] = Folder(self._df.at[i, 'folder_name'],
                                                                                  self._folder_tree[self._df.at[i, 'parent']],
                                                                                  self._df.at[i, 'readme_text'])
                except NameError as err:
                    # It's possible that children folders are entered before their parent in the look-up table (LUT)
                    # This shouldn't be discouraged, since LUT creation should be more flexible for the designer.
                    # If this does occur, then search for a LUT entry with that parent name & add it to the tree.
                    # To prevent this issue from cascading to the next parent, check dictionary existence recursively
                    # until the root directory is reached.
                    names: pd.Series = self._df.loc['folder_names']
                    if not names[names == self._df.at[i, 'parent']].empty:
                        index = names[names == self._df.at[i, 'folder_name']].index[0]
                    else:

                    print('Dictionary key not yet created: ', err)
                else:
                    folder_add_flag = True  # breaks the while loop so for loop moves onto next folder_name




if __name__ == '__main__':
    proj = ProjectTemplate('data_science_project_template.csv')
    proj.create_project_tree()


