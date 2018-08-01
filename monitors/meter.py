class TopkMeter(object):
    def __init__(self, topk=[1]):
        self.topk = topk
        self.meters = {k: Meter() for k in topk}

    def update(self, preds, target, batch_size=256):
        maxk = max(self.topk)
        batch_size = target.size(0)

        _, pred = preds.topk(maxk, 1, True, True)
        pred = pred.t()
        correct = pred.eq(target.view(1, -1).expand_as(pred))

        for k in self.topk:
            correct_k = correct[:k].view(-1).float().sum(0, keepdim=True)
            self.meters[k].update(correct_k, batch_size)

    def mean(self):
        return {k: self.meters[k].mean() for k in self.topk}

    def reset(self):
        for meter in self.meters.values():
            meter.reset()


class Meter(object):
    def __init__(self):
        self.count = 0.
        self.total = 0.

    def update(self, v, count):
        self.count += count
        self.total += v

    def mean(self):
        return self.total / self.count

    def reset(self):
        self.count = 0
        self.total = 0
