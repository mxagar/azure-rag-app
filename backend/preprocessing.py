from abc import abstractmethod
from typing import Union
from enum import Enum
from langchain.schema import Document
from langchain.document_loaders import PyPDFLoader, CSVLoader, TextLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Format(Enum):
    PDF = 1
    CSV = 2
    MARKDOWN = 3
    TEXT = 4
    WEB = 5


def suffix2format(suffix: str) -> Format:
    suffix = suffix.lower()
    if suffix == "pdf":
        return Format.PDF
    elif suffix == "csv":
        return Format.CSV
    elif suffix in ("txt", "text"):
        return Format.TEXT
    elif suffix in ("md", "markdown"):
        return Format.MARKDOWN
    elif suffix in ("http", "https", "html", "web", "url"):
        return Format.WEB
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


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
    def __init__(self):
        super().__init__()

    def load(self, file_path: str) -> list[Document]:
        loader = PyPDFLoader(file_path)
        return loader.load()


class CSVPreprocessor(Preprocessor):
    def __init__(self):
        super().__init__()

    def load(self, file_path: str) -> list[Document]:
        loader = CSVLoader(file_path)
        return loader.load()


class TextPreprocessor(Preprocessor):
    def __init__(self):
        super().__init__()

    def load(self, file_path: str) -> list[Document]:
        loader = TextLoader(file_path)
        return loader.load()


class WebPreprocessor(Preprocessor):
    def __init__(self):
        super().__init__()

    def load(self, url: str) -> list[Document]:
        loader = WebBaseLoader(url)
        return loader.load()


def get_preprocessor(
    suffix: Union[str, Format],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Preprocessor:
    if isinstance(suffix, str):
        suffix = suffix2format(suffix)
    if suffix == Format.PDF:
        return PDFPreprocessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif suffix == Format.CSV:
        return CSVPreprocessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif suffix in (Format.TEXT, Format.MARKDOWN):
        return TextPreprocessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif suffix in (Format.WEB):
        return WebPreprocessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
