#!/bin/bash
# Git auto commit va push scripti

# Loyihadagi o‘zgarishlarni ko‘rsatish
git status

# Barcha o‘zgarishlarni qo‘shish
git add .

# Commit xabarini foydalanuvchidan olish yoki default qilib "update"
commit_message=${1:-"update"}

# Commit qilish
git commit -m "$commit_message"

# Main branchga push qilish
git push origin main
