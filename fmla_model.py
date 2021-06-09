#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 20:22:54 2021

@author: kevinbarker
"""

#Objects

class EventData:
    def __init__(self, start, end, accepted, hours):
        self.start = start
        self.end = end
        self.accepted = accepted
        self.hours = hours

class AvailabilityObject:
    def __init__(self, fmlaAccepted, partialAcceptance, requestedHours, acceptedHours, deniedHours, totalHoursUsed, remainingHours, message):
        self.fmlaAccepted = fmlaAccepted
        self.partialAcceptance = partialAcceptance
        self.requestedHours = requestedHours
        self.acceptedHours = acceptedHours
        self.deniedHours = deniedHours
        self.totalHoursUsed = totalHoursUsed
        self.remainingHours = remainingHours
        self.message = message