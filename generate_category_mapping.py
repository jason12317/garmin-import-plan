import json

# 讀取 exercise.json 檔案
with open('exercise.json', 'r') as f:
    data = json.load(f)

# 建立 mapping 表檔案
categories = data['categories']
output_lines = []

# 為每個 category 下的 exercise 建立 mapping
for category_name, category_info in sorted(categories.items()):
    if 'exercises' in category_info:
        exercises = category_info['exercises']
        # 添加 category 註解
        output_lines.append(f'# {category_name} Category')
        
        for exercise_name in sorted(exercises.keys()):
            # 建立 CATEGORY_EXERCISE_NAME 的格式
            key = f'{category_name}_{exercise_name}'
            output_lines.append(f'{key}={category_name}')
        
        output_lines.append('')  # 空行分隔不同 category

# 將 mapping 寫入檔案
with open('exercise_category_mapping.properties', 'w', encoding='utf-8') as f:
    f.write('# Exercise Category Mapping\n')
    f.write('# Format: CATEGORY_EXERCISE_NAME=CATEGORY\n')
    f.write('# Generated from exercise.json\n\n')
    f.write('\n'.join(output_lines))

print(f'已生成 exercise_category_mapping.properties 檔案')
print(f'總共包含 {len([line for line in output_lines if "=" in line])} 個 exercise mappings')