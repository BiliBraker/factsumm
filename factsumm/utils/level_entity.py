from typing import Dict, List, Tuple

from transformers import LukeForEntityPairClassification, LukeTokenizer, pipeline


def load_ner(model: str) -> object:
    """
    Load Named Entity Recognition model from HuggingFace hub

    Args:
        model (str): model name to be loaded

    Returns:
        object: Pipeline-based Named Entity Recognition model

    """
    print("Loading Named Entity Recognition Pipeline...")

    return pipeline(
        task="ner",
        model=model,
        tokenizer=model,
        framework="pt",
        grouped_entities=True,
    )


def load_rel(model: str):
    """
    Load LUKE for Relation Extraction model and return its applicable function

    Args:
        model (str): model name to be loaded

    Returns:
        function: LUKE-based Relation Extraction function

    """
    print("Loading Relation Extraction Pipeline...")

    tokenizer = LukeTokenizer.from_pretrained(model)
    model = LukeForEntityPairClassification.from_pretrained(model)

    def extract_relation(sentences: List) -> List[Tuple]:
        """
        Extraction Relation based on Entity Information

        Args:
            sentence (str): original sentence containing context
            head_entity (Dict): head entity containing position information
            tail_entity (Dict): tail entity containing position information

        Returns:
            List[Tuple]: list of (head_entity, relation, tail_entity) formatted triples

        """
        triples = list()

        for sentence in sentences:
            tokens = tokenizer(
                sentence["text"],
                entity_spans=[
                    (sentence["spans"][0][0], sentence["spans"][0][-1]),
                    (sentence["spans"][-1][0], sentence["spans"][-1][-1]),
                ],
                return_tensors="pt",
            )
            outputs = model(**tokens)
            predicted_id = int(outputs.logits[0].argmax())
            relation = model.config.id2label[predicted_id]

            if relation != "no_relation":
                triples.append((
                    sentence["text"]
                    [sentence["spans"][0][0]:sentence["spans"][0][-1]],
                    relation,
                    sentence["text"]
                    [sentence["spans"][-1][0]:sentence["spans"][-1][-1]],
                ))

        return triples

    return extract_relation