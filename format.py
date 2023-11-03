from os import walk

i = 0
for (dirpath, dirnames, filenames) in walk("./src/content/blog"):
    for file in filenames:
      newContent = "---\n"
      with open('./src/content/blog/{}'.format(file), "r") as f:
        _ = f.readline()
        line = f.readline()
        while line != '':
          if "+++" in line:
            newContent += "---"
            line = f.readline()
            continue

          if "[taxonomies]" in line:
            line = f.readline()
            continue

          if "[extra]" in line:
            line = f.readline()
            continue

          newLine = line.replace(" = ", ": ")
          newContent += newLine
          line = f.readline()
          continue
      
      with open('./src/content/blog/{}'.format(file), "w") as f:
        f.write(newContent)


      i = i + 1
print('total {}'.format(i))