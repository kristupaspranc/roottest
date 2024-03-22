import pytest

import ROOT

import DistRDF


class TestRunGraphs:
    """Tests usage of RunGraphs function with Dask backend"""

    def test_rungraphs_dask_3histos(self, payload):
        """
        Submit three different Dask RDF graphs concurrently
        """
        # Create a test file for processing
        treename = "tree"
        filename = "../data/ttree/distrdf_roottest_check_rungraphs.root"
        nentries = 10000
        connection, backend = payload
        if backend == "dask":
            RDataFrame = ROOT.RDF.Experimental.Distributed.Dask.RDataFrame
            df = RDataFrame(treename, filename, npartitions=2,
                            daskclient=connection)
        elif backend == "spark":
            RDataFrame = ROOT.RDF.Experimental.Distributed.Spark.RDataFrame
            df = RDataFrame(treename, filename, npartitions=2,
                            sparkcontext=connection)
        histoproxies = [
            df.Histo1D((col, col, 1, 40, 45), col)
            for col in ["b1", "b2", "b3"]
        ]

        # Before triggering the computation graphs values are None
        for proxy in histoproxies:
            assert proxy.proxied_node.value is None

        DistRDF.RunGraphs(histoproxies)

        # After RunGraphs all histograms are correctly assigned to the
        # node objects
        for proxy in histoproxies:
            histo = proxy.proxied_node.value
            assert isinstance(histo, ROOT.TH1D)
            assert histo.GetEntries() == nentries
            assert histo.GetMean() == 42


if __name__ == "__main__":
    pytest.main(args=[__file__])