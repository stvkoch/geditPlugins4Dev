#!/usr/bin/env ruby

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


# Usage: just run the script, it'll generate a data/ directory

require 'rdoc/ri/ri_paths'
require 'rdoc/ri/ri_descriptions'
require 'rdoc/markup/simple_markup/to_flow'
require 'fileutils'
require 'yaml'

require 'rexml/document'

module CommentParser
    def comment_parser(comment)
      output = ""
      if comment.nil?
        output << "<p>No description for this element</p>"
      else
        comment.each do |part|
          output << parse_element(part)
        end
      end
      output
    end

    def parse_element(elem)
      output = ""
      if elem.instance_of? SM::Flow::P
        output << %Q[<p>#{elem.body}</p>]
      elsif elem.instance_of? SM::Flow::VERB
        output << %Q[<pre>#{elem.body}</pre>]
      elsif elem.instance_of? SM::Flow::H
        level = elem.level
        text = elem.text
        output << %Q[<h#{level}>#{text}</h#{level}>]
      elsif elem.instance_of? SM::Flow::LI
        output << %Q[<li>#{elem.body}</li>]
      elsif elem.instance_of? SM::Flow::RULE
        output << '<hr />'
      else
        output << '<ul>'
        elem.contents.each do |item|
          output << parse_element(item)
        end
        output << '</ul>'
      end
      output
    end

    def filter_symbols(str)
      output = str
      output = output.gsub(/(%3f)/, "?")
      output = output.gsub(/(%26)/, "&")
      output = output.gsub(/(%2a)/, "*")
      output = output.gsub(/(%2b)/, "+")
      output = output.gsub(/(%2d)/, "-")
      output = output.gsub(/(%3c)/, "<")
      output = output.gsub(/(%3d)/, "=")
      output = output.gsub(/(%3e)/, ">")
      output = output.gsub(/(%5b)/, "[")
      output = output.gsub(/(%5d)/, "]")
      output = output.gsub(/(%7c)/, "|")
      output = output.gsub(/(%60)/, "`")
      output = output.gsub(/(%21)/, "!")
      output = output.gsub(/(%40)/, "@")
      output = output.gsub(/(%25)/, "%")
      output = output.gsub(/(%7e)/, "~")
      output = output.gsub(/(%2f)/, "/")
      output = output.gsub(/(%5e)/, "^")
      output
    end
end

class MethodDesc
  include CommentParser

  attr_reader :name, :is_class_method, :file_name, :comment, :is_public

  def initialize(path, name, is_class_method)
    @name = name
    @is_class_method = is_class_method

    separator = ""
    separator = "/" if path[-1] != "/"

    if is_class_method
        type = "c"
    else
        type = "i"
    end
    @file_name = path

    method_desc = YAML.load_file(@file_name)


    @is_public = method_desc.visibility == "public"
    @comment = comment_parser(method_desc.comment)
  end

end

class ClassDesc
  include CommentParser

  attr_reader :name, :class_path, :comment, :inner_classes

  def initialize(path, class_name)
    @name = class_name

    separator = ""
    separator = "/" if path[-1] != "/"

    temp_name = class_name.split("::")[-1]

    @class_path = "#{path}#{separator}#{temp_name}/"

    class_desc = YAML.load_file(@class_path +  "cdesc-#{temp_name}.yaml")
    @comment = comment_parser(class_desc.comment)
    @inner_classes = ClassDesc::get_classes_in_folder(@class_path, @name)

    @inner_classes = @inner_classes.sort { |a, b|
        a.name <=> b.name
    }

    @methods = read_methods().sort { |a, b|
        # class methods should be over
        if a.is_class_method and not b.is_class_method:
            -1
        elsif not a.is_class_method and b.is_class_method:
            1
        else
            a.name <=> b.name
        end
    }

  end

  def read_methods
    methods = []
    Dir.foreach(@class_path) do |entry|
      full_path = @class_path + entry
      if not File.directory? full_path
        # Entry cannot be class description
        if entry !~ /(cdesc-)(.*)(\.yaml)/
            match = /(.*)(-)(.)(\.yaml)/.match(entry)
            method_name = filter_symbols(match[1])
            is_class_method = match[3] == "c"
            methods << MethodDesc::new(full_path, method_name, is_class_method)
        end
      end
    end
    methods
  end

  def self.get_classes_in_folder(path, basename = nil)
    classes = []
    Dir.foreach(path) do |entry|
      full_path = path + entry
      if File.directory? full_path and entry != "." and entry != ".."
        # this is a class, create
        if basename.nil?
          classes << ClassDesc::new(path, entry)
        else
          classes << ClassDesc::new(path, "#{basename}::#{entry}")
        end
      end
    end
    classes
  end

  def to_s
    output = ""
    output << "#{@name}\n"

    @methods.each do |method|
      if method.is_public:
        method.is_class_method ? symbol = "::" : symbol = "#"
        output << "#{@name}#{symbol}#{method.name}\n"
      end
    end

    @inner_classes.each do |klass|
      output << klass.to_s
    end
    output
  end

  def write_help_xml(base_dir, overwrite=false)
    last_name = @name.split("::")[-1]
    path = "#{base_dir}/#{last_name}/"
    #puts path

    begin
      FileUtils::mkdir path
    rescue
    end

    if File.exist? "#{path}/#{last_name}.xml" and not overwrite
      puts "Skipped merging: " + @name
      return
#      xmldoc = REXML::Document.new(File.open("#{path}/#{last_name}.xml"))
#      methods_root = REXML::XPath.first(xmldoc, "//help/methods")
    else
      # Create the XML doc
      xmldoc = REXML::Document.new

      # Write the declaration
      xmldecl = REXML::XMLDecl.new("1.0", "UTF-8", "no")
      xmldoc.add xmldecl


      # Add root
      root = REXML::Element.new "help"
      xmldoc.add_element root

      # Add comment
      comment_node = REXML::Element.new "comment"
      comment_node.text = @comment
      root.add_element comment_node

      methods_root = REXML::Element.new "methods"
      root.add_element methods_root
    end

    @methods.each do |method|
      if method.is_public:
        method_node = REXML::Element.new "method"

        method_node.attributes["name"] = method.name
        method_node.text = method.comment

        methods_root.add_element method_node
      end
    end

    xmldoc.write(File.open("#{path}/#{last_name}.xml", "w"), 0)

    @inner_classes.each do |klass|
      klass.write_help_xml(path)
    end

  end
end

OUTPUT_DIR = "./data/"


puts "RDoc to XML help data v 0.1 - by Vinícius Baggio Fuentes"

############################################################ Load RI Data

puts "Loading RI information..."

classes = []


# Read classes from all RI available path's
#RI::Paths::PATH.each() do |path|
# classes << ClassDesc.get_classes_in_folder(path + "/")
#end

if RI::Paths::SYSDIR != []
  classes << ClassDesc.get_classes_in_folder(RI::Paths::SYSDIR + "/")
  classes = classes.flatten
elsif RI::Paths::SITEDIR != []
  classes << ClassDesc.get_classes_in_folder(RI::Paths::SITEDIR + "/")
  classes = classes.flatten
elsif RI::Paths::GEMSDIR != []
  classes << ClassDesc.get_classes_in_folder(RI::Paths::GEMSDIR + "/")
  classes = classes.flatten
elsif RI::Paths::HOMEDIR != []
  classes << ClassDesc.get_classes_in_folder(RI::Paths::HOMEDIR + "/")
  classes = classes.flatten
end

# Sort them
classes = classes.sort { |a, b|
  a.name <=> b.name
}

############################################################ Write info
FileUtils::rmtree OUTPUT_DIR # clean old data

FileUtils::mkdir OUTPUT_DIR

puts "Writing Topics..."
topics = File.new("topics", "w")
classes.each do |klass|
  topics.puts klass
  klass.write_help_xml(OUTPUT_DIR)
end
