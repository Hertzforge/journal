-- Turns an article's figures and tables into what each output needs.
--
-- A figure is written as an ordinary image of its picture, in either of two forms:
--
--   ![Caption.](figures/name.png){#fig-name fig-alt="What the figure shows." data="data/file.csv"}
--   ![What the figure shows.](figures/name.png)        (the caption is the author's next paragraph)
--
-- A figure the build drew from code/name.py has figures/name.json beside its picture. On a page
-- the picture is then joined by the interactive figure, which is written into the page so nothing
-- is fetched; with scripts off, or in print, the picture is what shows. A picture supplied with
-- the article is shown as it is. Either way the figure offers its data, its code and its picture.
-- In the PDF the picture is used as it is.
--
-- A table is put in a frame of its own, so a wide one scrolls inside the frame on a narrow screen
-- and the page does not.
--
-- _figures.json (written by the build) says what each figure is. HF_VARIANT says which page is
-- being built: "page" (the article page, files beside it) or "single" (the one-file download,
-- where the build embeds each linked file).

local variant = os.getenv("HF_VARIANT") or "page"

local figures = {}
do
  local file = io.open("_figures.json", "r")
  if file then
    figures = pandoc.json.decode(file:read("a")) or {}
    file:close()
  end
end

local function escape(text)
  return (text:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function read(path)
  local file = io.open(path, "r")
  if not file then return nil end
  local text = file:read("a")
  file:close()
  return text
end

local function kind(path)
  return (path:match("%.([%w]+)$") or "file"):upper()
end

local function download(href, label)
  local name = href:match("([^/]+)$")
  local embed = (variant == "single") and " data-hf-embed" or ""
  return '<a href="' .. escape(href) .. '" download="' .. escape(name) .. '"' .. embed .. '>' .. label .. '</a>'
end

function Image(img)
  local figure = figures[img.src]
  if not figure then return nil end

  if quarto.doc.is_format("typst") then
    if not img.attributes.width then img.attributes.width = "100%" end
    if figure.alt ~= "" and not img.attributes["fig-alt"] then img.attributes["fig-alt"] = figure.alt end
    return img
  end
  if not quarto.doc.is_format("html") then return nil end

  local links = {}
  for _, file in ipairs(figure.data) do
    local label = (#figure.data > 1) and (file:match("([^/]+)$") or file) or ("Data (" .. kind(file) .. ")")
    table.insert(links, download(file, label))
  end
  if figure.code ~= "" then table.insert(links, download(figure.code, "Code")) end
  table.insert(links, download(img.src, "Picture (" .. kind(img.src) .. ")"))
  local offered = '<p class="hf-figure-links">This figure: ' .. table.concat(links, " ") .. '</p>'
  local picture = '<img class="hf-static" src="' .. escape(img.src) .. '" alt="' .. escape(figure.alt) .. '">'

  local html
  if figure.drawn then
    local spec = read("figures/" .. figure.name .. ".json")
    if not spec then
      error("figures/" .. figure.name .. ".json is missing; code/" .. figure.name .. ".py did not draw it")
    end
    -- A figure's text must never end the script element it is written into.
    spec = spec:gsub("</", "<\\/")
    html = table.concat({
      '<div class="hf-figure" data-figure="' .. escape(figure.name) .. '">',
      '<div class="hf-plot" role="img" aria-label="' .. escape(figure.alt) .. '" hidden></div>',
      picture,
      '<script type="application/json" class="hf-spec">' .. spec .. '</script>',
      offered,
      '</div>',
    }, "\n")
  else
    html = table.concat({
      '<div class="hf-figure hf-figure-given" data-figure="' .. escape(figure.name) .. '">',
      picture,
      offered,
      '</div>',
    }, "\n")
  end
  return pandoc.RawInline("html", html)
end

-- A figure that stands alone in its paragraph is a block, not a line of text.
function Para(para)
  local only = para.content[1]
  if #para.content == 1 and only.t == "RawInline" and only.format == "html" and only.text:match('^<div class="hf%-figure') then
    return pandoc.RawBlock("html", only.text)
  end
end

function Table(tbl)
  if not quarto.doc.is_format("html") then return nil end
  return pandoc.Div({ tbl }, pandoc.Attr("", { "table-wrap" }, { style = "--cols: " .. #tbl.colspecs }))
end
