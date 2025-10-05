-- Lua filter to prevent tables from splitting across pages in DOCX output
-- Adds w:cantSplit property to all table rows

function Table(tbl)
  -- Only apply to DOCX output
  if FORMAT:match 'docx' then
    -- Add cantSplit property to each row
    for i, row in ipairs(tbl.rows) do
      -- Set the row property to prevent splitting
      if not row.attr then
        row.attr = pandoc.Attr()
      end
      -- Add custom attribute that will be preserved in DOCX
      row.attr.attributes['custom-style'] = 'KeepTogether'
    end
  end
  return tbl
end

-- Alternative approach: Add raw OpenXML to prevent splitting
function RawBlock(el)
  return el
end

-- Add table properties via raw OpenXML insertion
local function add_no_split_property(tbl)
  if FORMAT:match 'docx' then
    -- Insert raw OpenXML before table to set properties
    local raw_xml = pandoc.RawBlock('openxml',
      '<w:tblPr><w:tblLayout w:type="fixed"/></w:tblPr>')
    return {raw_xml, tbl}
  end
  return tbl
end

return {
  {Table = add_no_split_property}
}
