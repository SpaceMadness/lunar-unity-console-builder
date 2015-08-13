require_relative 'copyright_param'

class Copyright

  attr_reader :text, :params

  def initialize(text)

    @text = text
    @params = []

  end

  def add_param(param)
    @params.push param
  end

  def set_param(name, value)

    @params.each do |param|
      if name == param.name
        param.value = value
        return
      end
    end

    add_param CopyrightParam.new(name, value)

  end

  def process

    new_text = text

    @params.each do |param|
      name = param.decorated_name
      value = param.value

      new_text = new_text.sub name, value

    end

    return new_text

  end

  def self.remove_header_comment(text)

    lines = text.lines "\n"

    index = find_first_non_comment_line_index lines
    return text if index == 0

    lines = lines[index..lines.length]
    return lines.join

  end

  def self.find_first_non_comment_line_index(lines)
    comment_found = false
    multiline = false
    skip_blank_lines = false

    lines.each_with_index do |line, index|

      stripped_line = line.strip

      if skip_blank_lines
        return index if stripped_line.length > 0
        next
      end

      if comment_found
        skip_blank_lines = multiline ? stripped_line.end_with?('*/') : !stripped_line.start_with?('//')
      else # comment not found
        multiline = stripped_line.start_with? '/*'
        comment_found = multiline || stripped_line.start_with?('//')

        unless comment_found
          return index if stripped_line.length > 0
          skip_blank_lines = true
        end
      end

    end

    return 0 # no comment found
  end

end