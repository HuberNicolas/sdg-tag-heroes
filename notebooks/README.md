# Notebooks

Exploration notebooks from the master's thesis, kept with their outputs. They document how parts of the system came
about. The application does not use any of them. Ruff does not check this folder.

There are two kinds:

- **Local notebooks** import `db`, `models` and `settings` from this repository. They need the databases of the
  original dataset, so they do not run with the [dummy dataset](../README.md#dummy-dataset).
- **Colab notebooks** are self-contained. They install their packages with `!pip install` and load public datasets,
  or a model file you upload yourself.

## Data and models

| Notebook | What it does | Relevance |
|---|---|---|
| [`topic_model.ipynb`](topic_model.ipynb) | BERTopic on the ZORA abstracts: embeddings, UMAP, HDBSCAN and KMeans, topic names with GPT. Writes [`topic_data.json`](topic_data.json) | **High.** Exploration behind the topic collections ([docs](../docs/dataset.md)) |
| [`model_comparison.ipynb`](model_comparison.ipynb) | Compares the SDG predictions of Aurora and Dvdblk as histograms, and tries rescaling and softmax variants. Writes [`sdg_histograms/`](sdg_histograms) | **High.** Led to the 0.85 rescaling in [`load_mariadb_scaler.py`](../utils/mariadb/load_mariadb_scaler.py) and the model choice |
| [`exploration.ipynb`](exploration.ipynb) | First BERTopic run on the publications in Qdrant, with interactive Plotly maps | Medium. Earlier step before `topic_model.ipynb` |
| [`publication_comparison.ipynb`](publication_comparison.ipynb) | Compares the publication IDs in MariaDB and Qdrant (missing and added) | Low. One-off consistency check |
| [`osdg_dataset_exploration.ipynb`](osdg_dataset_exploration.ipynb) (Colab) | SDG and agreement distribution in the [OSDG Community Dataset](https://zenodo.org/communities/osdg) | Low. Early look at an SDG dataset with labels from people; the system uses ZORA |

## System design

| Notebook | What it does | Relevance |
|---|---|---|
| [`xp_scores.ipynb`](xp_scores.ipynb) (Colab) | Designs the score for an SDG label from the number of votes and the model confidence: bootstrap, interest and luck terms | **High.** The formula and parameters are in [`scoring_service.py`](../services/scoring_service.py) |
| [`glyph_generator.ipynb`](glyph_generator.ipynb) (Colab) | Draws the hexagon glyph of the 17 SDGs with matplotlib | **High.** Prototype of the glyphs in [`frontend/composables/glyph/`](../frontend/composables/glyph) |
| [`glyph_experiments.ipynb`](glyph_experiments.ipynb) (Colab) | Compares ways to show the 17 SDG prediction values: radar and bar charts, circular glyphs, a flower, hexagon grids, barcodes | **High.** Led to the hexagon glyph |

## Early experiments

Done at the start of the thesis to learn the methods. Most run on toy datasets, not on SDG data.

| Notebook | What it does | Relevance |
|---|---|---|
| [`aurora_xai.ipynb`](aurora_xai.ipynb) (Colab) | LIME, Anchors and SHAP on the Aurora SDG 1 model (`sdg1.h5`, not included) for sample abstracts | Medium. Showed that SHAP works on text; the system shows SHAP explanations ([`sdg_explanations.py`](../api/app/routes/sdg_explanations.py)) |
| [`xai_mnist_lime_shap.ipynb`](xai_mnist_lime_shap.ipynb) (Colab) | Trains a small MNIST model (two models averaged, federated style) and explains it with LIME and SHAP | Low. Learning exercise |
| [`xai_mnist_shap.ipynb`](xai_mnist_shap.ipynb) (Colab) | SHAP DeepExplainer on an MNIST CNN, after the SHAP tutorial | Low. Learning exercise |
| [`active_learning_cifar10.ipynb`](active_learning_cifar10.ipynb) (Colab) | Uncertainty sampling with modAL on CIFAR-10. The model stays at about 10 % accuracy, so the setup does not work | Low. First attempt at active learning; the system uses the entropy of the SDG predictions instead ([`metrics_service.py`](../services/metrics_service.py)) |

## Data in the outputs

The outputs of the local notebooks show titles and abstracts of ZORA publications. The outputs of
`osdg_dataset_exploration.ipynb` show text excerpts from the OSDG Community Dataset (CC BY 4.0). See
[License](../README.md#license).
