-- Lua filter to apply custom table style to all tables
-- This filter sets the 'solvengineTable' style for all Table elements
-- when converting to DOCX format

function Table(elem)
  -- Apply the solvengineTable style to all tables
  elem.attributes['custom-style'] = 'solvengineTable'
  return elem
end
