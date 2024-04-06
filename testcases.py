from lab7 import PRC

def test_case_1():
    # create a PRC object
    prc = PRC(2, 2)
    # create a graph
    prc.create_graph('samples/2/graph.txt')
    prc.process_parcels('samples/2/bookings.txt')
    prc.run_simulation(3)
    assert prc.all_parcels_delivered() == False
    assert 'P2Ludhiana4' in prc.get_stranded_parcels()

    prc.run_simulation(4)
    assert 'P2Ludhiana4' not in prc.get_stranded_parcels()

    # delete the prc object
    del prc

def test_case_2():
    # create a PRC object
    prc = PRC(5,5)
    # create a graph
    prc.create_graph('samples/5/graph.txt')
    prc.process_parcels('samples/5/bookings.txt')
    prc.run_simulation(4)
    assert prc.all_parcels_delivered() == False
    assert 'P31' not in prc.get_delivered_parcels()
    assert len(prc.get_parcels_delivered_upto_time_tick(3)) == 25

def test_case_3():
    # create a PRC object
    prc = PRC(2, 2)
    # create a graph
    prc.create_graph('samples/1/graph.txt')
    prc.process_parcels('samples/1/bookings.txt')
    prc.run_simulation(20)
    assert prc.time_tick < 20
    
def test_case_4():
    # create a PRC object
    prc = PRC(5,5)
    # create a graph
    prc.create_graph('samples/3/graph.txt')
    prc.process_parcels('samples/3/bookings.txt')

    # read the graph file and check if the graph is created correctly
    assert len(prc.graph.vertices) == 30
    assert len(prc.graph.edges) == 119

def test_case_5():

    # create a PRC object
    prc = PRC(5,5)
    # create a graph
    prc.create_graph('samples/4/graph.txt')
    prc.process_parcels('samples/4/bookings.txt')
    # print(prc.graph.bfs("Mumbai","Ahmedabad"))
    # check bfs 
    assert prc.graph.bfs('Mumbai', 'Ahmedabad') == ['Mumbai', 'Nashik', 'Ahmedabad']

def test_case_6():

    # create a PRC object
    prc = PRC(5,5)
    # create a graph
    prc.create_graph('samples/4/graph.txt')
    prc.process_parcels('samples/4/bookings.txt')

    assert "Tirupati" not in prc.graph.dfs('Chennai', "Rohtak")

# run the test cases
# test_case_1()
# test_case_2()
test_case_3()
test_case_4()
test_case_5()
test_case_6()
