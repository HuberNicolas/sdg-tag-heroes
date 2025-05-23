from app.explainers import (
    get_explainer,
)
from lxt.models.bert import (
    BertForSequenceClassification as BertForSequenceClassificationLRP,
)
from transformers import AutoTokenizer
import torch
import os
from db.mongodb_connector import client as mclient

class Args:
    def __init__(self):
        self.model_family = None
        self.tfidf_corpus_path = None

model_path = "dvdblk/scibert_sdg_cased_zo-up"

id2label = {i: str(i + 1) for i in range(17)}
label2id = {str(i + 1): i for i in range(17)}

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model = BertForSequenceClassificationLRP.from_pretrained(
                model_path, id2label=id2label, label2id=label2id
            )
model = model.to(device)
tokenizer = AutoTokenizer.from_pretrained(model_path, do_lower_case=False)


args = Args()
args.model_family = "scibert"
args.tfidf_corpus_path = "./experiments/data/osdg.csv"

torch.cuda.init()
visible_devices_str = os.getenv("CUDA_VISIBLE_DEVICES")
if visible_devices_str is not None:
    visible_devices = [int(x) for x in visible_devices_str.split(",")]
else:
    visible_devices = list(range(torch.cuda.device_count()))
print(visible_devices)

explainer = get_explainer("shap-partition-tfidf", model, tokenizer, device, args)





import time
import gc
from sqlalchemy.orm import sessionmaker
# Establish MariaDB connection
from db.mariadb_connector import engine as mariadb_engine

Session = sessionmaker(bind=mariadb_engine)
# Create Session
session = Session()
from models.base import Base
from models.author import Author
from models.division import Division
from models.faculty import Faculty
from models.institute import Institute
from models.sdg_prediction import SDGPrediction
from models.sdg_label import SDGLabel
from models.sdg_label_history import SDGLabelHistory
from models.sdg_label_decision import SDGLabelDecision
from models.sdg_user_label import SDGUserLabel
from models.dim_red import DimRed
from models.publication import Publication
from db.qdrantdb_connector import client as qdrantdb_client
from tqdm import tqdm

metadata_publications = session.query(Publication).all()

# In db 111167

# oai:www.zora.uzh.ch:231667
metadata_publications_filtered = [pub for pub in metadata_publications if pub.oai_identifier_num > 231667 ]

print(len(metadata_publications))
print(len(metadata_publications_filtered))

print(111167 + len(metadata_publications_filtered))

metadata_publications = metadata_publications_filtered

db = mclient['igcl']
collection = db['sdg_shap_explanation']


def round_array(arr):
    def round_element(element):
        if isinstance(element, float):
            return round(element, 12)
        elif isinstance(element, (list, tuple)):
            return [round_element(item) for item in element]
        else:
            return element

    return [round_element(item) for item in arr]

for publication in tqdm(metadata_publications):
    explanation = explainer.explain(publication.title + " " + publication.description)

    doc = {"id": publication.oai_identifier, "input_tokens": explanation.input_tokens, "token_scores": round_array(explanation.token_scores), "base_values": round_array(explanation.additional_values["base_values"]), "xai_method": explanation.xai_method, "prediction_model": model_path}
    db.sdg_explanations.insert_one(doc)
    


