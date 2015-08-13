class CopyrightParam

  attr_accessor :name, :value

  def initialize(name, value)
    @name = name
    @value = value
  end

  def decorated_name
    "${#{@name}}"
  end

  def to_s
    "{#{@name}:#{@value}}"
  end

end