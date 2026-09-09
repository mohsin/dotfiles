-- Loaded on the VeryLazy event. LazyVim's defaults: https://www.lazyvim.org/keymaps
local map = vim.keymap.set

-- Strip trailing whitespace, keeping the cursor and the last search (was ,ss in .vimrc)
vim.api.nvim_create_user_command("StripWhitespace", function()
	local view = vim.fn.winsaveview()
	vim.cmd([[keeppatterns %s/\s\+$//e]])
	vim.fn.winrestview(view)
end, {})
map("n", "<leader>cw", "<cmd>StripWhitespace<cr>", { desc = "Strip trailing whitespace" })
