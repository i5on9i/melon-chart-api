#encoding=utf-8


from datetime import datetime, timedelta
import requests
from lxml import etree
from io import StringIO, BytesIO


class ChartType(object):
    WEEK = "WE"

class MelonChart(object):
    melonSearchChartUrl = "http://www.melon.com/chart/search/list.htm"

    def __init__(self):
        self.tree = None

    def getChart(self, sdate, edate):
        """
            Retrieve the chart list between {sdate} and {edate}
            Then, set {self.tree}

            :param sdate datetime
            :param edate datetime
        """
        sdateStr = sdate.strftime("%Y%m%d")
        edateStr = edate.strftime("%Y%m%d")
        dayVal = "{sdate}^{edate}"\
                .format(sdate=sdateStr, edate=edateStr)
        
        ageVal = sdate.year // 10 * 10

        options = {
            "chartType" : ChartType.WEEK,
            "age" : ageVal,
            "year" : sdate.year,
            "mon" : "%02d"%(sdate.month,),
            "day" : dayVal, # "20160307%5E20160313"
            "classCd" : "DP0100",
            "startDay" : sdateStr,
            "endDay" : edateStr,
            "moved" : "Y",
        }
        r = requests.get(self.melonSearchChartUrl, params=options)
        if r.status_code != 200:
            raise requests.RequestException()
        
        # self._saveAsFile(r.content)
        content = r.content.decode('utf-8')
        parser = etree.HTMLParser()
        self.tree   = etree.parse(StringIO(content), parser)

        return self


    def _saveAsFile(self, content):
        with open('r.htm', 'w+') as wf:
            wf.write(content.decode('utf-8'))
        
    def getRank(self, title):
        """
            :return rank int
        """
        
        tree = self.tree
        xpath = '//a[contains(text(), "{title}")]/ancestor::tr'.format(title=title)
        tr = tree.xpath(xpath)
        if len(tr) == 0:
            return None
        ranks = tr[0].xpath('.//span[contains(@class, "rank")]')
        
        return int(ranks[0].text)


def main():
    melonSearchChartUrl = "http://www.melon.com/chart/search/list.htm"


    # sdate = datetime(2016, 3, 7)
    # edate = datetime(2016, 3, 13)
    sdate = datetime(2016, 5, 23)
    edate = datetime(2016, 5, 29)
    tdelta = timedelta(days=7)
    
    mchart = MelonChart()
    while True:

        rank = mchart.getChart(sdate, edate).getRank("벚꽃 엔딩")
        print("sdate = {sdate}".format(sdate=sdate))
        print(rank)

        sdate = sdate + tdelta
        edate = edate + tdelta

    

if __name__ == '__main__':
    main()