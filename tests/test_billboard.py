import billboard

def test_hot_100_download():
  cd = billboard.ChartData('hot-100')
  assert len(cd) == 100
