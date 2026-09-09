-- Loaded before lazy.nvim starts. LazyVim's defaults: https://www.lazyvim.org/configuration/general
-- Only what differs from LazyVim, carried over from the old .vimrc and .editorconfig.
local opt = vim.opt

opt.background = "dark"
opt.expandtab = false -- real tabs, as .editorconfig says; projects with their own .editorconfig win
opt.tabstop = 2
opt.shiftwidth = 2
opt.gdefault = true -- :s replaces every match on the line unless told otherwise
opt.listchars = { tab = "▸ ", trail = "·", eol = "¬", nbsp = "_" }
opt.scrolloff = 3
opt.title = true

-- Format on demand with <leader>cf rather than on every save (Zed is set the same way)
vim.g.autoformat = false
