"""This module contains the implementation of
document loading and preprocessing (splitting into chunks).

The ingestion of the chunks happens elsewhere.

Supported formats:
- PDF
- CSV
- Text: TXT, Markdown
- Web

Author: Mikel Sagardia
Date: 2025-01-17
"""
from abc import abstractmethod
from typing import Union
from enum import Enum
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Format(Enum):
    PDF = 1
    CSV = 2
    MARKDOWN = 3
    TEXT = 4
    WEB = 5


def infer_format(format: str) -> Format:
    format = format.lower()
    
    if format.endswith(".pdf") or format == "pdf":
        return Format.PDF
    elif format.endswith(".csv") or format == "csv":
        return Format.CSV
    elif format.endswith(".txt") or format == "txt":
        return Format.TEXT
    elif (
        format.endswith(".md") 
        or format.endswith(".markdown") 
        or format == "md"
        or format == "markdown"
    ):
        return Format.MARKDOWN
    elif (
        format.startswith("http")
        or format.endswith(".html")
        or format.endswith(".htm")
        or "://" in format
        or format == "web"
        or format == "url"
    ):
        return Format.WEB
    else:
        raise ValueError(f"Unsupported file format: {format}")


class Preprocessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        pass

    @abstractmethod
    def load(self, file_path: str) -> list[Document]:
        raise NotImplementedError("The `load` method must be implemented in subclasses.")

    def split(self, documents: list[Document]) -> list[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        return text_splitter.split_documents(documents)

    def load_split(self, file_path: str) -> list[Document]:
        documents = self.load(file_path)
        return self.split(documents)


class PDFPreprocessor(Preprocessor):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def load(self, file_path: str) -> list[Document]:
        loader = PyPDFLoader(file_path)
        return loader.load()


class CSVPreprocessor(Preprocessor):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def load(self, file_path: str) -> list[Document]:
        loader = CSVLoader(file_path)
        return loader.load()


class TextPreprocessor(Preprocessor):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def load(self, file_path: str) -> list[Document]:
        loader = TextLoader(file_path)
        return loader.load()


class WebPreprocessor(Preprocessor):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def load(self, url: str) -> list[Document]:
        loader = WebBaseLoader(url)
        return loader.load()


def get_preprocessor(
    format: Union[str, Format],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Preprocessor:
    if isinstance(format, str):
        format = infer_format(format)
    if format == Format.PDF:
        return PDFPreprocessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif format == Format.CSV:
        return CSVPreprocessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif format in (Format.TEXT, Format.MARKDOWN):
        return TextPreprocessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif format == Format.WEB:
        return WebPreprocessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
