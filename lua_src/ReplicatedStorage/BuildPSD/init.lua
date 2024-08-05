local HttpService = game:GetService("HttpService")
local StarterGui = game:GetService("StarterGui")

local ProcessType = require(script:WaitForChild("ProcessType"))

local function make(layer, top)
	local frame = Instance.new(layer.ClassName)
	for property, value in pairs(layer.Properties) do
		if ProcessType[property] then
			value = ProcessType[property](value)
		end
		frame[property] = value
	end
	return frame
end

local function makeAll(layer, parent, top)
	local frame = make(layer, top)
	for _, child in pairs(layer.Children) do
		makeAll(child, frame)
	end
	frame.Parent = parent
	return frame
end

local function build(top)
	---local top = HttpService:JSONDecode(json)
	return makeAll(top, StarterGui, true)
end

return build