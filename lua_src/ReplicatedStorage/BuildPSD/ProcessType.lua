function udim(arr)
	return UDim.new(unpack(arr))
end

function udim2(arr)
	return UDim2.new(unpack(arr))
end

function colorSequence(sequences)
	local arr = {}
	for _, data in sequences do
		arr[#arr + 1] = ColorSequenceKeypoint.new(data[1], color3(data[2]))
	end
	return ColorSequence.new(arr)
end

function color3(str)
	if type(str) == "table" then
		return colorSequence(str)
	end
	local arr = {}
	for match in string.gmatch(str, "%-*%d[%d.]*") do
		arr[#arr + 1] = match
	end
	return Color3.fromRGB(unpack(arr))
end


--[[ ColorSequence.new({
    ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 153, 0)),
    ColorSequenceKeypoint.new(0.28, Color3.fromRGB(255, 186, 83)),
    ColorSequenceKeypoint.new(1, Color3.fromRGB(255, 255, 255)),
}) ]]

local module = {}

module.Position = udim2
module.Size = udim2
module.TextColor3 = color3
module.TextStrokeColor3 = color3
module.TextSize = tonumber
module.Color = color3
module.BackgroundColor3 = color3
module.CornerRadius = udim

return module