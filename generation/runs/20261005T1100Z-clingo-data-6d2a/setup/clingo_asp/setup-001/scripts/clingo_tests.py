"""Run tests/test_solvers.py restricted to clingo_asp: metadata tests, then the clingo container subtests."""
import os, sys, unittest

if __name__ == "__main__":
    sys.path.insert(0, r"C:\Users\kostis\code\DCP-Bench-Open")
    os.environ["DCP_CONTAINER_TESTS"] = "1"
    import tests.test_solvers as ts
    loader = unittest.TestLoader()
    ok = unittest.TextTestRunner(verbosity=2).run(loader.loadTestsFromTestCase(ts.MetadataTests)).wasSuccessful()
    ts.PILOTS = {"clingo_asp": ts.PILOTS["clingo_asp"]}
    suite = unittest.TestSuite([ts.ContainerTests(name) for name in ("test_pilots", "test_maximization", "test_missing_image")])
    ok &= unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    sys.exit(0 if ok else 1)
