import collections
from gaussian_blur3d_starter import gaussian_blur3d
from gaussian_blur3d_starter import pre_gaussian_blur3d
from gaussian_blur3d_starter import post_gaussian_blur3d

# Create a namedtuple type as the entries in a job registry
JobEntry = collections.namedtuple('JobEntry',
                                  'name, config, preprocess, postprocess, func')
class InferencePipeline:
    def __init__(self, registry: list):
        self.__job_dict__ = dict()
        for job in registry:
            self.__job_dict__[job.name] = job
#         registry.add 

    def register(self, job: JobEntry):
        if job is not None:
            self.__job_dict__[job.name] = job

    def unregister(self, job_name: str):
        try:
            del self.__job_dict__[job_name]
        except KeyError:
            print('Key Error: job name is not found!')
            pass

    def is_job_registered(self, job_name: str) -> bool:
        return job_name in self.__job_dict__

    def execute(self, job_name: str, in_dicom_dir: str, out_dicom_dir: str):
        if self.is_job_registered(job_name):
            print('Start executing %s!' % (job_name))
            job = self.__job_dict__[job_name]
            print('Runing %s\'s preprocess' % (job_name))
            job.preprocess(in_dicom_dir)
            print('Runing %s\'s postprocess' % (job_name))
            print('Runing %s\'s function' % (job_name))
            
        '''Execute a job specified by job_name, with the in_dicom_dir
        (directory containing DICOM files) as input and out_dicom_dir as the
        output DICOM directory.

        :param job_name: a string, the job's unique name
        :param in_dicom_dir: a string, the path to the input DICOM folder
        :param out_dicom_dir: a string, the path to the output DICOM folder
        '''
# if __name__ == 'main':
    
job0 = JobEntry(name='3dblur', config={'sigma': 1.0},
                    preprocess=pre_gaussian_blur3d,
                    postprocess=post_gaussian_blur3d,
                    func=gaussian_blur3d)
job1 = JobEntry(name='3dblur', config={'sigma': 2.0},
                    preprocess=pre_gaussian_blur3d,
                    postprocess=post_gaussian_blur3d,
                    func=gaussian_blur3d)
pipeline = InferencePipeline([job0, job1])
print(pipeline.__job_dict__)
job2 = JobEntry(name='3d', config={'sigma': 1.0},
                    preprocess=pre_gaussian_blur3d,
                    postprocess=post_gaussian_blur3d,
                    func=gaussian_blur3d)
pipeline.register(job2)
pipeline.execute('3dblur', './dicom_data', './dicom_output')