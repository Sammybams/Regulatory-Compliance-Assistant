compliance_classifier_schema = {
  "title": "extraction_result_articles_with_paragraphs",
  "description": "Articles each with a list of paragraphs (integers) and matched sectors. Arrays may be empty.",
  "type": "object",
  "properties": {
    "articles": {
      "type": "array",
      "minItems": 0,
      "items": {
        "type": "object",
        "properties": {
          "article": { "type": "integer", "minimum": 1 },
          "paragraphs": {
            "type": "array",
            "minItems": 0,
            "items": { "type": "integer", "minimum": 1 }
          }
        },
        "required": ["article", "paragraphs"],
        "additionalProperties": False
      },
      "description": "List of article objects. Each object has 'article' (int) and 'paragraphs' (array of ints)."
    },
    "sectors": {
      "type": "array",
      "minItems": 0,
      "items": {
        "type": "string",
        "enum": [
          "Government & Public Sector",
          "Health & Medical Services",
          "Finance & Banking",
          "Telecommunications & Digital Infrastructure",
          "Cybersecurity & National Security",
          "Research, Education & Statistics"
        ]
      }
    }
  },
  "required": ["articles", "sectors"],
  "additionalProperties": False
}



compliance_classifier = {
  "format": {
    "type": "json_object",
    "json_schema": {
        "name": "extraction_result_integers",
        "strict": True,
        "schema": compliance_classifier_schema
      }
  }
}


translation_format = {
  "format": {
    "type": "json_object",
    "json_schema": {
      "name": "translation_only",
      "strict": True,
      "schema": {
        "type": "object",
        "properties": {"translation": {"type": "string"}},
        "required": ["translation"],
        "additionalProperties": False
      },
    }
  }
}