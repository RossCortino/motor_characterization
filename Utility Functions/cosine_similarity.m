function output = cosine_similarity(A,B)
        if size(A,2) > 1
            A = A';
            
        end

        if size(B,2) > 1
            B = B';
        end

        assert(size(A,2) == 1, "Input A must be a vector")
        assert(size(B,2) == 1, "Input B must be a vector")
        assert(size(A,1) == size(B,1),"Vectors A & B must be the same length")

        numerator = A'*B;
        denominator = norm(A,2)*norm(B,2);

        output = numerator/denominator;
end