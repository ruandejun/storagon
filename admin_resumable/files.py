# -*- coding: utf-8 -*-
import fnmatch, re

from django.core.files.base import File


class ResumableFile(object):

    def __init__(self, storage, kwargs):
        self.storage = storage
        self.kwargs = kwargs
        self.chunk_suffix = "_part_"

    @property
    def chunk_exists(self):
        """Checks if the requested chunk exists.
        """
        resumableCurrentChunkSize = int(self.kwargs.get('resumableCurrentChunkSize', 1024 * 1024))

        chunk = "%s%s%s" % (
            self.identifierName,
            self.chunk_suffix,
            self.kwargs.get('resumableChunkNumber').zfill(4)
        )
        if self.storage.exists(chunk):
            size = self.storage.size(chunk)
            if size > 0 and size >= resumableCurrentChunkSize and size < resumableCurrentChunkSize+16:
                return True
            # if size>0:return True;
            self.storage.delete(chunk)  # else: remove error chunk
            print(u"Remove eror chunk!")
        return False

    @property
    def chunk_names(self):
        """Iterates over all stored chunks.
        """
        resumableTotalChunks = int(self.kwargs.get('resumableTotalChunks', 0))
        chunks = []
        files = sorted(self.storage.listdir('')[1])
        for file in files:
            if fnmatch.fnmatch(file, '%s%s*' % (self.identifierName,
                                                self.chunk_suffix)):
                m = re.search(r'part_0*(\d+?)', file);
                try:
                    chunkNumber = int(m.group(1));
                except:
                    chunkNumber=0;
                if chunkNumber>0 and chunkNumber <= resumableTotalChunks:
                    chunks.append(file)
        return chunks

    def chunks(self):
        """Iterates over all stored chunks.
        """
        resumableTotalChunks = int(self.kwargs.get('resumableTotalChunks', 0))
        files = sorted(self.storage.listdir('')[1])
        for file in files:
            if fnmatch.fnmatch(file, '%s%s*' % (self.identifierName,
                                                self.chunk_suffix)):
                m = re.search(r'part_0*(\d+?)', file);
                try:
                    chunkNumber = int(m.group(1));
                except:
                    chunkNumber=0;
                if chunkNumber>0 and chunkNumber <= resumableTotalChunks:
                    yield self.storage.open(file, 'rb').read()

    def delete_chunks(self):
        [self.storage.delete(chunk) for chunk in self.chunk_names]

    @property
    def file(self):
        """Gets the complete file.
        """
        if not self.is_complete:
            raise Exception('Chunk(s) still missing')

        return self

    @property
    def filename(self):
        """Gets the filename."""
        filename = self.kwargs.get('resumableFilename')
        if not filename or '/' in filename:
            raise Exception('Invalid filename')
        return "%s_%s" % (
            self.kwargs.get('resumableTotalSize'),
            filename.encode('utf-8')
        )

    @property
    def identifierName(self):
        """Gets the filename."""
        identifierName = self.kwargs.get('resumableIdentifier')
        if not identifierName or '/' in identifierName:
            raise Exception('Invalid identifierName')
        return identifierName;

    @property
    def is_complete(self):
        """Checks if all chunks are already stored.
        """
        resumableTotalSize = int(self.kwargs.get('resumableTotalSize', 0))
        resumableTotalChunks = int(self.kwargs.get('resumableTotalChunks', 0))
        # print u"Current FileSize=%s"%(self.size)
        return self.size >= resumableTotalSize and resumableTotalSize > 0 and len(self.chunk_names) == resumableTotalChunks

    def process_chunk(self, file):
        chunk = "%s%s%s" % (
            self.identifierName,
            self.chunk_suffix,
            self.kwargs.get('resumableChunkNumber').zfill(4)
        )
        if self.storage.exists(chunk):
            self.storage.delete(chunk)
        return self.storage.save(chunk, file)

    @property
    def size(self):
        """Gets chunks size.
        """
        size = 0
        # print self.chunk_names;
        for chunk in self.chunk_names:
            size += self.storage.size(chunk)
        return size
