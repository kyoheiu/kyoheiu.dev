from os import walk

i = 0
for (dirpath, dirnames, filenames) in walk("./src/content/blog"):
    for file in filenames:
      with open('./src/content/blog/{}'.format(file), "r+") as f:
        newContent = "---\n"
        _ = f.readline()
        line = f.readline()
        while line != '':
          if "+++" in line:
            newContent += "---"
            line = f.readline()
            continue

          if "taxonomies" in line:
            line = f.readline()
            continue

          newLine = line.replace(" = ", ": ")
          newContent += newLine
          line = f.readline()
          continue

        f.write(newContent)

      i = i + 1
print('total {}'.format(i))