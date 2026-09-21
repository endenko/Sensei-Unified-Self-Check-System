#!/usr/bin/env python3
"""Test suite for Sensei Unified Self-Check System"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import (
    Problem, ProblemType, Difficulty, 
    AlgebraGenerator, GeometryGenerator,
    registry, app, ProblemRequest
)
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def algebra_gen():
    return AlgebraGenerator()

class TestAlgebraGenerator:
    def test_generate_linear_easy(self, algebra_gen):
        problems = algebra_gen.generate("linear_equation", Difficulty.EASY, 3)
        assert len(problems) == 3
        for p in problems:
            assert p.type == ProblemType.SHORT_ANSWER
            assert p.difficulty == Difficulty.EASY
            assert "x" in p.question.lower()
            assert isinstance(p.correct_answer, (int, float))
    
    def test_generate_quadratic_medium(self, algebra_gen):
        problems = algebra_gen.generate("quadratic_equation", Difficulty.MEDIUM, 2)
        assert len(problems) == 2
        for p in problems:
            assert "x" in p.question.lower() or "bậc hai" in p.question.lower()
    
    def test_generate_factoring(self, algebra_gen):
        problems = algebra_gen.generate("factoring", Difficulty.EASY, 1)
        assert len(problems) == 1
        assert "phân tích" in problems[0].question.lower() or "nhân tử" in problems[0].question.lower()
    
    def test_generate_system(self, algebra_gen):
        problems = algebra_gen.generate("system_of_equations", Difficulty.MEDIUM, 1)
        assert len(problems) == 1
        assert "hệ" in problems[0].question.lower()
    
    def test_invalid_topic(self, algebra_gen):
        with pytest.raises(ValueError):
            algebra_gen.generate("invalid_topic", Difficulty.EASY, 1)
    
    def test_validate_correct_answer(self, algebra_gen):
        prob = algebra_gen.generate("linear_equation", Difficulty.EASY, 1)[0]
        is_valid = algebra_gen.validate(prob.correct_answer, prob)
        assert is_valid is True
    
    def test_validate_wrong_answer(self, algebra_gen):
        prob = algebra_gen.generate("linear_equation", Difficulty.EASY, 1)[0]
        is_valid = algebra_gen.validate(prob.correct_answer + 1000, prob)
        assert is_valid is False

class TestGeometryGenerator:
    def test_generate_triangle_area(self):
        gen = GeometryGenerator()
        problems = gen.generate("triangle_area", Difficulty.MEDIUM, 2)
        assert len(problems) == 2
        for p in problems:
            assert "tam giác" in p.question.lower()
            assert isinstance(p.correct_answer, (int, float))
    
    def test_generate_circle(self):
        gen = GeometryGenerator()
        problems = gen.generate("circle", Difficulty.MEDIUM, 1)
        assert len(problems) == 1
        assert "tròn" in problems[0].question.lower() or "bán kính" in problems[0].question.lower()

class TestAPIEndpoints:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["name"] == "Sensei Unified Self-Check System"
    
    def test_list_generators(self, client):
        response = client.get("/generators")
        assert response.status_code == 200
        data = response.json()
        assert "generators" in data
        assert "algebra" in data["generators"]
    
    def test_generate_problem(self, client):
        request = ProblemRequest(
            type="short_answer",
            difficulty="easy",
            topic="linear_equation",
            count=2
        )
        response = client.post("/generate/problem", json=request.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["problems"]) == 2
    
    def test_generate_problem_invalid_difficulty(self, client):
        request = ProblemRequest(
            type="short_answer",
            difficulty="invalid",
            topic="linear_equation",
            count=1
        )
        response = client.post("/generate/problem", json=request.model_dump())
        assert response.status_code == 422 or response.status_code == 400
    
    def test_configure_api(self, client):
        response = client.post("/configure/api", json={
            "generator": "algebra",
            "endpoint_url": "https://api.example.com",
            "api_key": "test_key",
            "timeout": 60,
            "rate_limit": 50
        })
        assert response.status_code == 200
        assert response.json()["success"] is True

class TestProblemDataclass:
    def test_problem_to_dict(self):
        prob = Problem(
            id="test_id",
            type=ProblemType.MULTIPLE_CHOICE,
            difficulty=Difficulty.EASY,
            question="What is 2+2?",
            correct_answer=4,
            explanation="Simple addition",
            tags=["math", "addition"]
        )
        d = prob.to_dict()
        assert d["id"] == "test_id"
        assert d["type"] == "multiple_choice"
        assert d["difficulty"] == "easy"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])