import matplotlib.pyplot as plt
import json

if __name__ == '__main__':
    x = [None]
    y = [None]
    with open('euro-night-0000100.instance.json') as json_file:
        data = json.load(json_file)
        for p in data['points']:
            x.append(p['x'])
            y.append(p['y'])
            # print('%i: (%.1f | %.1f)' % (int(p['i']), float(p['x']), float(p['y'])))
    plt.plot(x,y, 'ro')
    plt.show()
