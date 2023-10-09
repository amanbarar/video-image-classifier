from dotenv import load_dotenv
import labelbox as lb
import json
import os

load_dotenv()

def setupProject(projectName , datasetName , batchName , ontologyName, video_path , ontology_path):

    project_details = {'workspace_api_key': os.environ['LB_API_KEY']}
    client = lb.Client(api_key= os.environ['LB_API_KEY'])

    project = client.create_project(name=projectName,
                                    media_type=lb.MediaType.Video)
    print(f'project created, Project ID: {project.uid}')
    project_details['project_id'] = {'project_name': project.name ,  'project_id': project.uid}

    dataset = client.create_dataset(name=datasetName)
    print(f'dataset created, Dataset ID: {dataset.uid}')
    project_details['dataset_id'] = {'dataset_name': dataset.name ,  'dataset_id': dataset.uid}

    video_file_paths = [os.path.abspath(os.path.join(video_path , video_file)) for video_file in os.listdir(video_path)]
    try:
        task = dataset.create_data_rows(video_file_paths)
        task.wait_till_done()
    except Exception as err:
        print(f'Error while creating labelbox dataset -  Error: {err}')
    print('datarows added to the dataset')
    batch = project.create_batch(
        name=batchName,
        data_rows=[data_row.uid for data_row in dataset.data_rows()],
        priority=1,
    )
    print(f'Batch created and added to the project. Batch ID: {batch.uid}')
    project_details['batch_id'] = {'batch_name': batch.name ,  'batch_id': batch.uid}

    with open(ontology_path , 'r') as f:
        normalized_ontology_schema = json.load(f)
    ontology = client.create_ontology(name=ontologyName,
                                  normalized=normalized_ontology_schema,
                                  media_type=lb.MediaType.Video)
    project.setup_editor(ontology)

    print('ontology added to the project')
    print("\nYour Project is ready to invite labelers and start the annotation Process.\n After onboarding the team members as labelers use the generated `project_details.json` file to fill up the google form and save it for later use.")

    with open('project_details.json' , 'w') as f:
        json.dump(project_details , f , indent=4)

    return project

if __name__ == "__main__":
    
    projectName = input('Project Name: ')
    datasetName = input('dataset Name: ')
    batchName = input('batch Name: ')
    video_folder_path = input('Path to the folder containing all videos: ')

    project = setupProject(projectName=projectName,  
                 datasetName=datasetName,
                 batchName=batchName,
                 ontologyName="object_detection_recognition_schema",
                 video_path=video_folder_path,
                 ontology_path="normalized_ontology_schema.json"
    )