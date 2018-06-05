import sys


# class test():
    
#     def __init__(self, inputs):
#         self.inputs = sy
    
    
    
    
if __name__ == '__main__':
    
    job_terms = []
    location_terms = []
    
    print(sys.argv[1])
    print(type(sys.argv[1]))
    
    try:
        with open(sys.argv[1]) as file:
            job_searches = file.readlines()

            for job_search in job_searches:
                keywords = job_search.split("-")
                job_terms.append(keywords[0].strip())
                location_terms.append(keywords[1].strip())
    except:
        print("Issue reading {}. Be sure path is correct and format is correct (see docs for details).".format(sys.argv[0]))
        
    print(job_terms)
    print(location_terms)