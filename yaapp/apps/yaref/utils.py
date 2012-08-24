import subprocess as sub

def convert_filename_to_filepath(filename):
    """
    123456789.jpg --> 123/456/789.jpg
    """
    if len(filename) != len('123456789.jpg'):
        return None
    part1 = filename[:3]
    part2 = filename[3:6]
    part3 = filename[6:9]
    extension = filename[-3:]
    return '%s/%s/%s.%s' % (part1, part2, part3, extension)

def convert_to_mp3(ffmpeg_bin, ffmpeg_options, source, destination):
    args = [ffmpeg_bin,
            '-i',
            source]
    args.extend(ffmpeg_options.split(" "))
    args.append(destination)
    p = sub.Popen(args,stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    if len(errors) == 0:
        return False
    return True
