import token_and_sim
import vector_Creation
from elmoformanylangs import Embedder
import time


if __name__ == '__main__':
    t0 = time.time()
    e = Embedder('..\\142')
    for id in range(11, 21):
        print ("############  AGB", id, " ############" )
        vector_Creation.create_meanVector_cleanedText(id, e)
        print("### Vector Creation ", time.time() - t0, "seconds wall time")
        token_and_sim.highest_similarity_paragraphs(id, 1)
        print("### Paragraph prediction ", time.time() - t0, "seconds wall time")
        token_and_sim.highest_similarity_clauses(id, 1)
        print("### Clause prediction ", time.time() - t0, "seconds wall time")
    print(time.time() - t0, "seconds wall time")
    print("Done")