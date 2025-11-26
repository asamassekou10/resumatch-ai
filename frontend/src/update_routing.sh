#!/bin/bash

# This script replaces setView() calls with navigate() calls

FILE="App.jsx"

# Create a temporary file
TMP=$(mktemp)

# Map view names to route paths
declare -A VIEW_MAP=(
    ["landing"]="/"
    ["login"]="/login"
    ["register"]="/register"
    ["dashboard"]="/dashboard"
    ["analyze"]="/analyze"
    ["result"]="/result"
    ["pricing"]="/pricing"
    ["admin"]="/admin"
    ["market-dashboard"]="/market/dashboard"
    ["skill-gap"]="/market/skill-gap"
    ["job-stats"]="/market/job-stats"
    ["skill-relationships"]="/market/skill-relationships"
)

# Read the file and replace
cp "$FILE" "$TMP"

for view in "${!VIEW_MAP[@]}"; do
    path="${VIEW_MAP[$view]}"
    sed -i "s/setView('$view')/navigate('$path')/g" "$TMP"
done

# Also handle setView(view === 'login' ? 'register' : 'login')
sed -i "s/setView(view === 'login' ? 'register' : 'login')/navigate(location.pathname === '\/login' ? '\/register' : '\/login')/g" "$TMP"

# Move the temp file back
mv "$TMP" "$FILE"

echo "Routing updated successfully!"
