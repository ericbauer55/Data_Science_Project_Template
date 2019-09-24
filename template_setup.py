from __future__ import annotations  # allows Folder to reference itself as a type
import os
from typing import Optional, List  # Optional is a type that could be None


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


def create_project(minimal: bool = False) -> None:
    # Read me strings and architecture are derived from:
    # 1. https://github.com/makcedward/ds_project_template
    # 2. http://projecttemplate.net/architecture.html

    # Create the minimal directories
    root = Folder('root', None, None)
    data = Folder('data', root, """Folder for storing subset data for experiments. 
                                It includes both raw data and processed data for temporary use.""""")
    raw = Folder('raw', data, """Storing the raw result which is generated from "preparation" folder code. 
                                My practice is storing a local subset copy rather than retrieving data from remote data 
                                store from time to time. It guarantees you have a static dataset for rest of action. 
                                Furthermore, we can isolate from data platform unstable issue and network 
                                latency issue.""")
    processed = Folder('processed', data, """To shorten model training time, it is a good idea to persist processed 
                                          data. It should be generated from 'processing' folder.""")
    src = Folder('src', root, """Stores source code (python, R etc) which serves multiple scenarios. During data 
                              exploration and model training, we have to transform data for particular purpose. 
                              We have to use same code to transfer data during online prediction as well. So it better
                              separates code from notebook such that it serves different purpose.""")
    preparation = Folder('preparation', src, """Data ingestion such as retrieving data from CSV, relational database, 
                                             NoSQL, Hadoop etc. We have to retrieve data from multiple sources all the 
                                             time so we better to have a dedicated function for data retrieval. """)
    processing = Folder('processing', src, """Data transformation/ processing in case it what the model or eda needs.
                                              Ideally, we have clean data that's rare. You may say that
                                              we should have data engineering team helps on data transformation. 
                                              However, we may not know what we need until studying the data. One of the
                                              important requirements is both off-line training and online prediction 
                                              should use same pipeline to reduce misalignment.""")
    modeling = Folder('modeling', src, """Model building source code. It should not just include model training part,
                                       but also evaluation part. On the other hand, we have to think about multiple 
                                       models scenario. Typical use case is ensemble model such as combing Logistic
                                        Regression model and Neural Network model.""")
    visualize = Folder('visualize', src, """Here you can store any graphs that you produce. Other code-driven
                                         visualizations or diagrams can be included here""")
    # If the project is meant to be created with limited folders, return now
    if minimal:
        return
    test = Folder('test', root, """In R&D, data science focus on building model but not make sure everything work well 
                                in unexpected scenario. However, it will be a trouble if deploying model to API. Also, 
                                test cases guarantee backward compatible issue but it takes time to implement it.""")
    model = Folder('model', root, """Folder for storing binary (json or other format) file for local use.""")
    notebook = Folder('notebook', root, """Storing all notebooks includeing EDA and modeling stage.""")
    eda = Folder('eda', notebook, """Exploratory Data Analysis (aka Data Exploration) is a step for exploring what you 
                                  have for later steps. For short term purpose, it should show what you explored. 
                                  Typical example is showing data distribution. For long term, it should store in 
                                  centralized place. """)
    evaluation = Folder('evaluation', notebook, """Besides modeling, evaluation is another important step. For people
                                                to trust the model, they must see how it performs""")
    modeling = Folder('modeling', notebook, """Notebook contains your  model building & training. """)
    poc = Folder('poc', notebook, """Occasionally, you have to do some PoC (Proof-of-Concept). It can be show in here 
                                  for temporary purposes.""")
    doc = Folder('doc', root, """Here you can store any documentation that you’ve written about your analysis. It can 
                              also be used as root directory for GitHub Pages to create a project website.""")
    profiling = Folder('profiling', root, """Here you can store any scripts you use to benchmark and time your code.""")
    logs = Folder('logs', root, """Here you can store a log file of any work you’ve done on this project.""")
    reports = Folder('reports', root, """Here you can store any output reports, such as HTML or LaTeX versions of 
                                      tables, that you produce.""")


if __name__ == '__main__':
    create_project()


