for notebook in docs/examples/*.ipynb; do
  uv run jupyter nbconvert --to=markdown "$notebook"  --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_all_outputs_tags remove_output
done
