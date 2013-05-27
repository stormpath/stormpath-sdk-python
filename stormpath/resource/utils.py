#
# Copyright 2012, 2013 Stormpath, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
module Stormpath
  module Resource
    module Utils
      include ActiveSupport::Inflector
      include Stormpath::Util::Assert

      def inspect
        ''.tap do |str|
          str << %Q[#<#{class_name_with_id} @properties={]
          @read_lock.lock
          begin
            str << properties.map do |key, value|
              if printable_property? key
                if value.kind_of? Hash and value.has_key? Stormpath::Resource::Base::HREF_PROP_NAME
                  value = %Q[{ "#{Stormpath::Resource::Base::HREF_PROP_NAME}" => "#{value[Stormpath::Resource::Base::HREF_PROP_NAME]}" }]
                end
                %Q["#{key} => #{value}"]
              end
            end.compact.join(',')
          ensure
            @read_lock.unlock
          end
          str << '}>'
        end
      end

      def to_s
        "#<#{class_name_with_id}>"
      end

      def to_yaml
        "--- !ruby/object: #{self.class.name}\n".tap do |yaml|
          @read_lock.lock

          begin
            properties_yaml = properties.each do |key, value|
              if printable_property? key
                " #{key}: #{value} \n"
              end
            end.compact.join("\n")
            unless properties_yaml.empty?
              yaml << " properties\n "
              yaml << properties_yaml
            end
          ensure
            @read_lock.unlock
          end
        end
      end

      def class_name_with_id
        object_id_hex = '%x' % (self.object_id << 1)
        "#{self.class.name}:0x#{object_id_hex}"
      end
    end
  end
end
