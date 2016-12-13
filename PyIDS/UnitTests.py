import unittest
import os
import numpy as np
import Neural_Network as NN
import Data_Reader as DR
import Network_Traffic_Reader as NTR

class Test_UnitTests(unittest.TestCase):

    def initNtr(self):
        ntr = NTR.Network_Traffic_Reader()
        return ntr

    def initDr(self):
        dr = DR.Data_Reader()
        return dr

    def initNn(self):
        nn = NN.Neural_Network(3, 12, 8, 1)
        return nn

    def calculateCorrectness(self, output, answers, ansKey):
        # Calculate correctness...
        right = 0
        total = 0
        for num, item in enumerate(output, 0):
            ans = str(answers[num][0])
            if str(np.around(item[0], 0)) == str(ans):
                right += 1
            total += 1
        percent = np.around((right/(total)) * 100, 2)
        return percent

    def test_NTR_getNextPacket(self):
        ntr = self.initNtr()
        pkt = None
        pkt = ntr.getNextPacket()
        self.assertIsNotNone(pkt)

    def test_NTR_getSinglePacket(self):
        ntr = self.initNtr()
        pkt = None
        pkt = ntr.getSinglePacket()
        self.assertIsNotNone(pkt)
        if "TCP" in pkt or "UDP" in pkt:
            pass
        else:
            self.fail("Packet did not contain acceptable types")

    def test_DR_readData(self):
        dataTypesFile = "dataTypesFile.txt"
        dataFile = "tmpMsg2.txt"

        dr = self.initDr()

        self.assertEqual(dr.data, {})
        self.assertEqual(dr.symbolicOptions, {})
        self.assertEqual(dr.answerTypes, [])
        self.assertEqual(dr.tcpFieldTypes, [])

        dr.readDataFiles(dataTypesFile, dataFile)

        self.assertNotEqual(dr.data, {})
        self.assertNotEqual(dr.symbolicOptions, {})
        self.assertNotEqual(dr.answerTypes, [])
        self.assertNotEqual(dr.tcpFieldTypes, [])

        self.assertEqual(dr.data, dr.get_data())

    def test_DR_getDataArray(self):
        dataTypesFile = "dataTypesFile.txt"
        dataFile = "tmpMsg2.txt"

        dr = self.initDr()

        self.assertEqual(dr.newDataArray, [])

        dr.readDataFiles(dataTypesFile, dataFile)

        self.assertEqual(dr.newDataArray, [])

        data = dr.get_data_array(True)

        self.assertNotEqual(data, [])
        self.assertNotEqual(dr.newDataArray, [])
        self.assertNotEqual(dr.newDataArray, data)

    def test_DR_getFullDataArray(self):
        dataTypesFile = "dataTypesFile.txt"
        dataFile = "tmpMsg2.txt"

        dr = self.initDr()

        self.assertEqual(dr.newFullDataArray, [])

        dr.readDataFiles(dataTypesFile, dataFile)

        self.assertEqual(dr.newFullDataArray, [])

        data = dr.get_full_data_array(True)

        self.assertNotEqual(data, [])
        self.assertNotEqual(dr.newFullDataArray, [])
        self.assertNotEqual(dr.newFullDataArray, data)

    def test_NN_trainAndCompute(self):
        dataTypesFile = "dataTypesFile.txt"
        dataFile = "tmpMsg2.txt"

        dr = self.initDr()
        nn = self.initNn()

        dr.readDataFiles(dataTypesFile, dataFile)
        data, answers, ansKey = dr.get_data_array(True)

        nn.train(data,answers,90)
        output = nn.compute(data)
        percent = self.calculateCorrectness(output, answers, ansKey)

        self.assertGreaterEqual(percent, 90)

    def test_NN_determineMalicious(self):
        dataTypesFile = "dataTypesFile.txt"
        dataFile = "tmpMsg2.txt"

        dr = self.initDr()
        nn = self.initNn()

        dr.readDataFiles(dataTypesFile, dataFile)
        data, answers, ansKey = dr.get_data_array(True)

        nn.train(data,answers,90)

        data = ['tcp', 'S0', '1']
        newData = dr.convertSymbolic(data)
        output = nn.compute(newData)

        self.assertEqual(str(np.around(output[0][0], 0)), "1.0")

if __name__ == '__main__':
    unittest.main()
