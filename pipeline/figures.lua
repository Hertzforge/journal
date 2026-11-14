-- Turns an article's figures into what each output needs.
--
-- An article writes a figure as an ordinary image of its static picture:
--
--   ![Caption.](figures/name.png){#fig-name fig-alt="What the figure shows." data="data/file.csv"}
--
-- On a page, the picture is joined by the interactive figure (drawn from figures/name.json, which
-- is written into the page so nothing is fetched) and by links to the figure's data, its code and
-- its picture. With scripts off, or in print, the picture is what shows. In the PDF the picture
-- is used as it is.
--
-- HF_VARIANT says which page is being built: "page" (the article page, files beside it) or
-- "single" (the one-file download, where the build embeds each linked file).

local variant = os.getenv("HF_VARIANT") or "page"

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

local function download(href, label)
  local name = href:match("([^/]+)$")
  local embed = (variant == "single") and " data-hf-embed" or ""
  return '<a href="' .. escape(href) .. '" download="' .. escape(name) .. '"' .. embed .. '>' .. label .. '</a>'
end

function Image(img)
  local name = img.src:match("^figures/([%w_%-]+)%.png$")
  if not name then return nil end

  if quarto.doc.is_format("typst") then
    if not img.attributes.width then img.attributes.width = "100%" end
    return img
  end
  if not quarto.doc.is_format("html") then return nil end

  local alt = img.attributes["fig-alt"] or img.attributes["alt"] or ""
  if alt == "" then
    error("figures/" .. name .. ".png has no alternative text (fig-alt)")
  end
  local spec = read("figures/" .. name .. ".json")
  if not spec then
    error("figures/" .. name .. ".json is missing; code/" .. name .. ".py did not draw it")
  end
  -- A figure's text must never end the script element it is written into.
  spec = spec:gsub("</", "<\\/")

  local links = {}
  local data = img.attributes["data"]
  if data and data ~= "" then
    local kind = (data:match("%.([%w]+)$") or "file"):upper()
    table.insert(links, download(data, "Data (" .. kind .. ")"))
  end
  table.insert(links, download("code/" .. name .. ".py", "Code"))
  table.insert(links, download("figures/" .. name .. ".png", "Picture (PNG)"))

  local html = table.concat({
    '<div class="hf-figure" data-figure="' .. name .. '">',
    '<div class="hf-plot" id="hf-plot-' .. name .. '" role="img" aria-label="' .. escape(alt) .. '" hidden></div>',
    '<img class="hf-static" src="figures/' .. name .. '.png" alt="' .. escape(alt) .. '" width="800">',
    '<script type="application/json" class="hf-spec">' .. spec .. '</script>',
    '<p class="hf-figure-links">' .. table.concat(links, " ") .. '</p>',
    '</div>',
  }, "\n")
  return pandoc.RawInline("html", html)
end
