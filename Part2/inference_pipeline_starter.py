import collections
from gaussian_blur3d_starter import run_gaussian_blur3d
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
        '''Execute a job specified by job_name, with the in_dicom_dir
        (directory containing DICOM files) as input and out_dicom_dir as the
        output DICOM directory.
        '''
        print(self.__job_dict__)
        if self.is_job_registered(job_name):
            print('Start executing %s!' % (job_name))
            job = self.__job_dict__[job_name]
            print('Runing %s\'s preprocess' % (job_name))
            job.preprocess(in_dicom_dir)
            print('Runing %s\'s postprocess' % (job_name))
            job.func()
            print('Runing %s\'s function' % (job_name))
            job.postprocess(out_dicom_dir)
            

if __name__ == '__main__':
    # for testing
    job0 = JobEntry(name='3dblur', config={'sigma': 1.0},
                        preprocess=pre_gaussian_blur3d,
                        postprocess=post_gaussian_blur3d,
                        func=run_gaussian_blur3d)
    job1 = JobEntry(name='3dblur', config={'sigma': 2.0},
                        preprocess=pre_gaussian_blur3d,
                        postprocess=post_gaussian_blur3d,
                        func=run_gaussian_blur3d)
    pipeline = InferencePipeline([job0, job1])
    print(pipeline.__job_dict__)
    job2 = JobEntry(name='3d', config={'sigma': 1.0},
                        preprocess=pre_gaussian_blur3d,
                        postprocess=post_gaussian_blur3d,
                        func=run_gaussian_blur3d)
    pipeline.register(job1)
    pipeline.execute('3dblur', './mytestfile.hdf5', './')