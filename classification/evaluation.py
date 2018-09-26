#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sklearn import metrics


def score(prediction, target):
    return metrics.f1_score(target, prediction, average='weighted')

def make_report(prediction, target, class_labels):
    return metrics.classification_report(prediction, target, target_names=class_labels)
