class InverseMapTransform(object):
    def __init__(self, originalMin, originalRange, scaleFactor = 255):
        self.scaleFactor   = 255
        self.originalMin   = originalMin
        self.originalRange = float(originalRange)

    def getNewLinearTerm(self, linearTerm):
        return self.scaleFactor * linearTerm / self.originalRange

    def getNewConstantTerm(self, linearTerm, constantTerm):
        return self.scaleFactor * ( - linearTerm * self.originalMin / self.originalRange  + constantTerm )
    
    def doMap(self, linearTerm, constantTerm):
        return ( self.getNewLinearTerm(linearTerm), self.getNewConstantTerm(linearTerm, constantTerm) )
