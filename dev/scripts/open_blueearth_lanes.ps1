
$windowName = "blueearth-cst-$([guid]::NewGuid().ToString('N'))"

wt.exe -w $windowName new-tab `
  --title "S1 | config-modularization" `
  --tabColor "#3B82F6" `
  --suppressApplicationTitle `
  -d "C:\Users\taner\workspace\.worktrees\blueearth_cst\session-1"

# Give the newly named Terminal window time to register.
Start-Sleep -Milliseconds 750

wt.exe -w $windowName new-tab `
  --title "S2 | todo-and-chores" `
  --tabColor "#F59E0B" `
  --suppressApplicationTitle `
  -d "C:\Users\taner\workspace\.worktrees\blueearth_cst\session-2"

wt.exe -w $windowName new-tab `
  --title "S3 | available" `
  --tabColor "#A855F7" `
  --suppressApplicationTitle `
  -d "C:\Users\taner\workspace\.worktrees\blueearth_cst\session-3"