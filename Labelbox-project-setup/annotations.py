from dotenv import load_dotenv 
from tqdm import tqdm
import pandas as pd
import youtube_dl
import cv2 as cv
import labelbox
import pickle
import json
import os

load_dotenv()

class videoAnnotations:
    def __init__(self):
        # Initialize class properties
        self.video_directory = "video_files"
        self.metadata_directory = "video_metadata"
        self.export_parameters = {
            "attachments": True,
            "metadata_fields": True,
            "data_row_details": True,
            "project_details": True,
            "label_details": True,
            "performance_details": True,
            "interpolated_frames": True
        }
        self.filter_parameters = {
            "last_activity_at": ["2000-01-01 00:00:00", "2050-01-01 00:00:00"],
            "label_created_at": ["2000-01-01 00:00:00", "2050-01-01 00:00:00"],
            # Uncomment if needed:
            # "data_row_ids": ["<data_row_id>", "<data_row_id>"],
            # "batch_ids": ["<batch_id>", "<batch_id>"],
        }

    def initialize_project(self, project_id):
        # Initialize project related properties
        self.project_id = project_id
        self.client = labelbox.Client(os.environ['LB_API_KEY'])
        self.project = self.client.get_project(self.project_id)
        self.ontology_uid = self.project.ontology().uid

        # Ensure required directories exist
        if not os.path.exists(self.video_directory):
            os.makedirs(self.video_directory)
        if not os.path.exists(self.metadata_directory):
            os.makedirs(self.metadata_directory)

    def download_video(self, url, path):
        # Configure YouTube downloader options
        ydl_options = {
            'format': 'best',
            'outtmpl': path,
        }

        # Use youtube_dl to download video
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.download([url])

    def get_project_details(self):
        # Export project details based on specified parameters and filters
        export_task = self.project.export_v2(params=self.export_parameters, filters=self.filter_parameters)
        export_task.wait_till_done()

        # Check for errors in export task
        if export_task.errors:
            print(export_task.errors)
            return None
        else:
            return export_task.result

    def export_for_annotation(self, email=None):

        # Process results for a given email
        results = self.get_project_details()
        for result in results:
            if result['projects'][self.project_id]['project_details']['workflow_status'] == 'DONE':
                if email == result['projects'][self.project_id]['labels'][0]['label_details']['created_by']:

                    data_row_id = result['data_row']['id']
                    # Save metadata to file
                    with open(os.path.join(self.metadata_directory, f'{data_row_id}.json'), 'w') as file:
                        json.dump(result['projects'][self.project_id], file, indent=4)
                    # Download associated video
                    self.download_video(result['data_row']['row_data'], os.path.join(self.video_directory, f'{data_row_id}.mp4'))


    def get_annotated_video(self , video_path , metadata_path):

        def get_frame_annotations(frame , frame_data):
            frame_annotations = {}
            frame_annotations['frame'] = frame

            for feature_id in frame_data['objects'].keys():
                object_ = frame_data['objects'][feature_id]
                frame_annotations[object_['name']] = object_['bounding_box']

                for classification in object_['classifications']:
                    frame_annotations[classification['name']] = classification['radio_answer']['name']

            return frame_annotations

        if os.path.exists(metadata_path):
            with open(metadata_path , 'r') as f:
                video_metadata = json.load(f)
        else:
            print("video metadata not found")
            return None

        if os.path.exists(video_path):
            cap = cv.VideoCapture(video_path)
            annotated_video = []
            frame_data = video_metadata['labels'][0]['annotations']['frames']
            frame_num = 1

            while cap.isOpened():
                ret , frame = cap.read()
                if ret:
                    annotated_video.append(get_frame_annotations(frame , frame_data[str(frame_num)]))

                else:
                    break

                frame_num += 1

            return annotated_video

        else:
            print("Video not found")
            return None

    def get_dataset(self , filename=None):
        dataset = []
        video_files = os.listdir(self.video_directory)
        for video_file in tqdm(video_files):
            data_row_id = os.path.splitext(video_file)[0]
            dataset += self.get_annotated_video(os.path.join(self.video_directory , video_file) , os.path.join(self.metadata_directory , data_row_id + ".json"))

        df = pd.DataFrame.from_records(dataset)

        if filename != None:
            with open(filename , 'wb') as f:
                pickle.dump(df , f)

        return df


if __name__ == "__main__":
    annotator = videoAnnotations()
    PROJECT_ID = '<Project-ID>'
    annotator.initialize_project(PROJECT_ID)
    user_email = "<labeller's email id>"
    annotator.export_for_annotation(user_email)
    annotator.get_dataset(filename='dataset.pkl')