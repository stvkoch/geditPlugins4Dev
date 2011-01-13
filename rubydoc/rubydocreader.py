# Copyright (C) 2007 Vinicius Baggio Fuentes
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import os # to get my topics and data
import xml.dom.minidom # Read documentation

# This class is responsible to read the documentation from the XML files
class RubyDocReader:
    DATA_DIR = ""
    CACHE_SIZE = 10 # 10 topics
    TOPICS_FILE = ""
    ROOT_PATH = ""
    with_cache = True
    cache = {}

###################################################################### __init__
    # Use base_dir to check for the XML help data
    def __init__(self, base_dir="data/", with_cache=True, cache_size=10, topics="topics"):
        self.ROOT_PATH = os.path.dirname(__file__) + "/"
        self.TOPICS_FILE = self.ROOT_PATH + topics
        self.DATA_DIR = self.ROOT_PATH + base_dir
        self.CACHE_SIZE = cache_size
        self.with_cache = with_cache

################################################################### get_help_on
    # Reads the doc_item help data
    # Check for _read_help_data for syntax
    def get_help_on(self, doc_item):
        if not self.with_cache:
            # Returns no cached data
            result = self._read_help_data(doc_item)
        else:
            try:
                # Try to provoke KeyError
                if self.cache[doc_item]:
                    pass

                # No KeyError, cache exist!
                result = self.cache[doc_item]

            except KeyError:
                # if cache is full, we eliminate one item, to add another
                if len(self.cache) >= self.CACHE_SIZE:
                    self.cache.popitem()

                result = self.cache[doc_item] = self._read_help_data(doc_item)

        return result

################################################################ _read_from_xml
    # Reads the XML file to extract help data
    def _read_from_xml(self, file_path, method=""):
        doc = xml.dom.minidom.parse(file_path)
        root_node = doc.childNodes[0] # help

        # There are only two nodes
        for node in root_node.childNodes:
             if node.localName == "comment":
                comment_node = node
             elif node.localName == "methods": # Avoid \n and other invalid nodes
                methods_node = node


        # if method is unset, we're looking for the class help
        if not method:
            text_node = comment_node.childNodes[0] # get the text data from the node
        else:
            # search for the method documentation
            for m_node in methods_node.childNodes:
                if m_node.localName == "method": # Avoid \n and other stuff
                    if m_node.getAttribute("name") == method:
                        # found our method, set text_node
                        text_node = m_node.childNodes[0]


        return text_node.nodeValue

################################################################ _get_help_data
    # Get the help data on topic specified in doc_item
    # Doc item is the RI way of specifing which topic
    # example: REXML::Element#add_attribute
    def _read_help_data(self, doc_item):
        # We need to construct the file path from the doc_item
        method = ""

        splitted_text = doc_item.split("#")
        classes = splitted_text[0] # If it's a method, extract all the classes
        try:
            method = splitted_text[1] # try to get method, if it exists
        except:
            method = ""

        class_path = classes.split("::")
        last_word_in_classes = class_path[-1]

        # If word[0] is lowercase, then it's not a class, it's a class method! Why?
        # Because ruby coding style says that all class names should not start
        # with lower case characters, and all system classes respect this.
        if last_word_in_classes[0].islower() or not last_word_in_classes[0].isalpha():
            method = class_path.pop() # Remove the last word and get it
            last_word_in_classes = class_path[-1] # "Update" it so the file is correct

        class_path = "/".join(class_path)
        file_path = "%s/%s/%s.xml" % (self.DATA_DIR, class_path, last_word_in_classes)

        return self._read_from_xml(file_path, method)

#################################################################### get_topics
    # Get the list of topics
    def get_topics(self):
        f = open(self.TOPICS_FILE)
        lines = f.readlines()
        f.close()
        return lines
